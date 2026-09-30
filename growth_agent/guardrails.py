"""Guardrails: deterministic checks every proposed experiment must pass.

The reasoning layer can propose anything. Nothing it proposes reaches a human
reviewer, let alone an ad platform, until this module has checked it. The best
possible verdict is "ready_for_human_review". There is no code path that
approves or launches.
"""
from __future__ import annotations

import re
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from .analysis.experiments import FILLER
from .analysis.metrics import safe_div, summarize
from .pipeline import Result


class Arm(BaseModel):
    """One side of a test. Fields left empty inherit the campaign default."""

    label: str
    description: str
    objective: str | None = None
    theme: str | None = None
    cta: str | None = None
    creative_id: str | None = None
    targeting: str | None = None   # free text, for audience-targeting tests; reviewed by a person


class ExperimentProposal(BaseModel):
    proposal_id: str
    title: str
    hypothesis: str
    platform: str
    audience: str
    region: str
    control: Arm
    variant: Arm
    primary_metric: str
    guardrail_metrics: list[str] = Field(default_factory=list)
    daily_budget_per_arm: float = Field(gt=0)
    runtime_days: int = Field(gt=0)
    decision_rule: str
    evidence_ids: list[str]
    retest_of: str | None = None
    status: str = "DRAFT"
    requires_human_approval: bool = True


class Finding(BaseModel):
    rule: str
    severity: Literal["block", "warn"]
    message: str


def _vocab(result: Result) -> dict[str, set[str]]:
    c = result.dataset.campaigns
    return {k: set(c[k].dropna().unique()) for k in ("platform", "audience", "region", "objective", "theme", "cta")}


def _differences(p: ExperimentProposal, creatives: pd.DataFrame) -> list[str]:
    """Which attributes differ between control and variant."""
    lib = creatives.set_index("creative_id")
    diffs = [f for f in ("objective", "theme", "cta", "targeting") if getattr(p.control, f) != getattr(p.variant, f)]
    ca, cb = p.control.creative_id, p.variant.creative_id
    if ca != cb and ca in lib.index and cb in lib.index:
        if lib.loc[ca, "format"] != lib.loc[cb, "format"]:
            diffs.append("format")
        if lib.loc[ca, "theme"] != lib.loc[cb, "theme"] and "theme" not in diffs:
            diffs.append("theme")
        if not {"format", "theme"} & set(diffs):
            diffs.append("creative")
    return diffs


def validate(proposal: dict | ExperimentProposal, result: Result) -> dict:
    """Check a proposed experiment. Returns a verdict with every reason."""
    cfg = result.config
    try:
        p = proposal if isinstance(proposal, ExperimentProposal) else ExperimentProposal(**proposal)
    except ValidationError as err:
        return {
            "proposal_id": proposal.get("proposal_id") if isinstance(proposal, dict) else None,
            "verdict": "blocked",
            "blocks": [{"rule": "schema", "severity": "block", "message": e["msg"] + f" ({'.'.join(map(str, e['loc']))})"} for e in err.errors()],
            "warnings": [],
            "computed": {},
            "requires_human_approval": True,
        }

    findings: list[Finding] = []
    block = lambda rule, msg: findings.append(Finding(rule=rule, severity="block", message=msg))
    warn = lambda rule, msg: findings.append(Finding(rule=rule, severity="warn", message=msg))
    ds, pack = result.dataset, result.pack
    vocab = _vocab(result)
    lib = ds.creatives.set_index("creative_id")
    exps = {e["experiment_id"]: e for e in result.experiments}

    # R1. Human in the loop is not negotiable ----------------------------------
    if not p.requires_human_approval:
        block("human_approval", "requires_human_approval cannot be switched off.")
    if p.status.upper() not in cfg.allowed_staging_statuses:
        block("human_approval", f"Status '{p.status}' is not allowed. The agent may only stage as {' or '.join(cfg.allowed_staging_statuses)}.")

    # R2. Optimize for business outcomes -----------------------------------------
    if p.primary_metric.lower().strip() not in cfg.outcome_metrics:
        block(
            "outcome_metric",
            f"Primary metric '{p.primary_metric}' is not a business outcome. Use one of: {', '.join(cfg.outcome_metrics)}. "
            "Click and lead metrics may be guardrails only.",
        )

    # R3. No invented segments or creative ------------------------------------------
    for field in ("platform", "audience", "region"):
        if getattr(p, field) not in vocab[field]:
            block("known_values", f"{field} '{getattr(p, field)}' does not exist in the data. Known: {sorted(vocab[field])}.")
    for arm in (p.control, p.variant):
        for field in ("objective", "theme", "cta"):
            v = getattr(arm, field)
            if v is not None and v not in vocab[field]:
                block("known_values", f"{arm.label}: {field} '{v}' does not exist in the data.")
        if arm.creative_id is not None:
            if arm.creative_id not in lib.index:
                block("known_values", f"{arm.label}: creative '{arm.creative_id}' is not in the creative library.")
                continue
            cr = lib.loc[arm.creative_id]
            if str(cr["status"]).lower() != "active":
                block("creative", f"{arm.label}: creative {arm.creative_id} is not active.")
            if not p.audience.startswith(str(cr["audience_group"])):
                block("creative", f"{arm.label}: creative {arm.creative_id} was made for {cr['audience_group']} audiences, not {p.audience}.")
            if arm.theme and arm.theme != cr["theme"]:
                block("creative", f"{arm.label}: creative {arm.creative_id} is a {cr['theme']} creative but the arm says {arm.theme}.")

    # R4. One variable at a time -----------------------------------------------------
    diffs = _differences(p, ds.creatives)
    if len(diffs) == 0:
        block("one_variable", "Control and variant are identical on offer, theme, CTA, creative and targeting.")
    elif len(diffs) > 1:
        block("one_variable", f"Control and variant differ on {', '.join(diffs)}. A result could not be attributed to one cause.")

    # R5. Budget ceilings ----------------------------------------------------------------
    total = p.daily_budget_per_arm * 2 * p.runtime_days
    if p.daily_budget_per_arm > cfg.max_daily_budget:
        block("budget", f"Daily budget per arm ${p.daily_budget_per_arm:,.0f} exceeds the ${cfg.max_daily_budget:,.0f} ceiling (the highest the team has run).")
    if total > cfg.max_total_test_budget:
        block("budget", f"Total test budget ${total:,.0f} exceeds the ${cfg.max_total_test_budget:,.0f} ceiling.")

    # R6. Long enough, and big enough, to read ----------------------------------------------
    if p.runtime_days < cfg.min_planned_runtime_days:
        block("runtime", f"Planned runtime of {p.runtime_days} days is under the {cfg.min_planned_runtime_days}-day minimum for a pipeline read.")
    bench = result.dataset.campaigns[~result.dataset.campaigns["data_quality_flag"].fillna("").str.contains("immature", case=False)]
    # Campaigns historically spend less than their budget; size the test on what will actually be spent.
    pacing = float((ds.daily.groupby("campaign_id")["spend"].mean() / ds.campaigns.set_index("campaign_id")["daily_budget"]).mean())
    cells = summarize(bench, ["platform", "objective"]).set_index(["platform", "objective"])
    plat = summarize(bench, "platform").set_index("platform")
    computed: dict = {"total_budget": total, "historical_pacing": pacing, "differs_on": diffs, "arms": {}}
    if p.platform in plat.index:
        for arm in (p.control, p.variant):
            row = cells.loc[(p.platform, arm.objective)] if arm.objective and (p.platform, arm.objective) in cells.index else plat.loc[p.platform]
            spend = p.daily_budget_per_arm * pacing * p.runtime_days
            exp_ql = safe_div(spend, row["cost_per_ql"]) or 0.0
            exp_opp = safe_div(spend, row["cost_per_opp"]) or 0.0
            computed["arms"][arm.label] = {"expected_spend": spend, "expected_qualified_leads": exp_ql, "expected_opportunities": exp_opp}
            if exp_ql < cfg.min_sample_size:
                need = cfg.min_sample_size * row["cost_per_ql"] / (pacing * p.runtime_days)
                block(
                    "sample_size",
                    f"{arm.label}: expect about {exp_ql:.0f} qualified leads, under the {cfg.min_sample_size} minimum. "
                    f"At this runtime it needs roughly ${need:,.0f} per day.",
                )
            elif exp_opp < cfg.min_expected_opportunities:
                warn(
                    "sample_size",
                    f"{arm.label}: expect about {exp_opp:.0f} opportunities. A pipeline read will be noisy below {cfg.min_expected_opportunities}; "
                    "consider qualified-lead rate as the decision metric with pipeline as confirmation.",
                )
    computed["earliest_readout_day"] = p.runtime_days + cfg.lead_maturity_days
    if not p.decision_rule.strip():
        block("decision_rule", "A decision rule must be written before launch, not after the results are in.")

    # R7. Evidence must exist, be valid, and be settled ----------------------------------------
    if not p.evidence_ids:
        block("evidence", "No evidence cited.")
    for eid in p.evidence_ids:
        if not pack.has(eid):
            block("evidence", f"Evidence id '{eid}' does not exist in the evidence pack.")
            continue
        if eid.startswith("EXP.") and eid[4:] in exps and not exps[eid[4:]]["usable_as_evidence"] and p.retest_of != eid[4:]:
            block("evidence", f"{eid} is a rejected experiment ({'; '.join(exps[eid[4:]]['reasons'][:2])}) and cannot support a recommendation.")
    cited = [pack.get(e) for e in p.evidence_ids if pack.has(e)]
    if cited and all(e.reliability in ("provisional", "data_quality") for e in cited):
        block("evidence", "Every cited item is provisional or a data-quality note. At least one settled finding is required.")

    # R8. Do not re-ask answered questions or repeat known losers ---------------------------------
    arm_values = {f: (getattr(p.variant, f), getattr(p.control, f)) for f in ("objective", "theme", "cta")}
    for dim in diffs:
        if dim not in arm_values:
            continue
        a, b = arm_values[dim]
        key = f"{dim}:{'|'.join(sorted([str(a), str(b)]))}"
        for e in exps.values():
            if e["comparison_key"] != key or p.retest_of == e["experiment_id"]:
                continue
            msg = (
                f"{e['experiment_id']} already tested {e['hypothesis']} ({e['logged_result']} {e['logged_lift_pct']:+.0f}%, rated {e['tier']})."
            )
            if e["tier"] == "trusted":
                block("settled_question", msg + " Set retest_of with a reason if a repeat is intended.")
            elif e["tier"] == "directional":
                warn("settled_question", msg + " A confirmation test is reasonable; say so by setting retest_of.")
    # Only the variant is checked: naming a known loser as the thing being beaten is fine.
    text = " ".join([p.variant.description, p.variant.targeting or ""]).lower()
    for e in exps.values():
        if e["parsed"] or not e["usable_as_evidence"] or str(e["logged_result"]).lower() != "loss":
            continue
        loser = FILLER.sub("", e["hypothesis"].lower().split(" vs ")[0]).strip()
        head = loser.split()[0]
        if re.search(rf"\b{re.escape(loser)}\b", text) or re.search(rf"\b{re.escape(head)}\b", text):
            named = e["hypothesis"].split(" vs ")[0]
            msg = f"The variant resembles '{named}', which lost in {e['experiment_id']} ({e['logged_lift_pct']:+.0f}%, rated {e['tier']})."
            (block if e["tier"] == "trusted" else warn)("known_loser", msg)

    blocks = [f.model_dump() for f in findings if f.severity == "block"]
    warnings = [f.model_dump() for f in findings if f.severity == "warn"]
    return {
        "proposal_id": p.proposal_id,
        "verdict": "blocked" if blocks else "ready_for_human_review",
        "blocks": blocks,
        "warnings": warnings,
        "computed": computed,
        "requires_human_approval": True,
    }
