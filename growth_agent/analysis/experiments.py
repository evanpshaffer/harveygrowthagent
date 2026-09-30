"""Decide which past experiments the agent is allowed to learn from.

The experiment log's own "result" and "confidence" columns are treated as
claims, not facts. Each experiment is re-scored on runtime, sample size and
metric quality, then checked against what campaigns actually did.
"""
from __future__ import annotations

import re

import pandas as pd

from ..config import Config
from ..connectors.base import Dataset
from ..evidence import EvidencePack
from .drivers import compare_arms

FILLER = re.compile(r"\b(messaging|targeting)\b")
PLATFORMS = ("Google", "LinkedIn", "Meta")


def parse_hypothesis(text: str, cfg: Config) -> dict | None:
    """Read an 'A vs B' hypothesis into a dimension and two values.

    Returns None when the arms are not something campaign data can observe
    (for example 'stock photo vs product UI'). Convention in the log: the
    first-named arm is the variant, so 'Win' means A beat B.
    """
    t = text.lower().replace(" - repeat", "").strip()
    scope: dict[str, str] = {}
    m = re.search(r"\s+for\s+(.+)$", t)
    if m:
        target = m.group(1).strip()
        t = t[: m.start()]
        for p in PLATFORMS:
            if target == p.lower():
                scope["platform"] = p
        if target in ("in-house", "in house"):
            scope["audience_group"] = "In-House"
        if target == "law firm":
            scope["audience_group"] = "Law Firm"
    if " vs " not in t:
        return None
    raw_a, raw_b = (FILLER.sub("", s).strip() for s in t.split(" vs ", 1))
    a, b = cfg.hypothesis_vocab.get(raw_a), cfg.hypothesis_vocab.get(raw_b)
    if not a or not b or a[0] != b[0]:
        return None
    return {"dimension": a[0], "a": a[1], "b": b[1], "scope": scope}


def comparison_key(hypothesis: str, parsed: dict | None) -> str:
    """Identity of the question being tested, used to find repeats."""
    if parsed:
        return f"{parsed['dimension']}:{'|'.join(sorted([parsed['a'], parsed['b']]))}"
    return hypothesis.lower().replace(" - repeat", "").strip()


def score(row: pd.Series, cfg: Config) -> tuple[str, list[str]]:
    """Return (tier, reasons). Tiers: trusted, directional, rejected."""
    hard, soft = [], []
    if row["runtime_days"] < cfg.min_runtime_days:
        hard.append(f"ran {int(row['runtime_days'])} days (minimum {cfg.min_runtime_days})")
    if row["sample_size"] < cfg.min_sample_size:
        hard.append(f"sample of {int(row['sample_size'])} (minimum {cfg.min_sample_size})")
    metric = str(row["primary_metric"]).lower().strip()
    if metric not in cfg.outcome_metrics:
        soft.append(f"primary metric '{row['primary_metric']}' is a proxy, not a business outcome")
    if str(row["confidence"]).lower() != "high":
        soft.append(f"logged confidence is {row['confidence']}")
    notes = str(row["notes"] or "")
    for p in PLATFORMS:
        if p.lower() in notes.lower() and p != row["platform"]:
            soft.append(f"notes describe {p} but the test is logged on {row['platform']}")
    if hard:
        return "rejected", hard + soft
    return ("directional", soft) if soft else ("trusted", [])


def observed_check(row: pd.Series, parsed: dict | None, bench: pd.DataFrame, cfg: Config) -> dict:
    """Does settled campaign data agree with the experiment's claim?"""
    if not parsed:
        return {"verdict": "not observable", "detail": "The arms are not a field in campaign data."}
    group = parsed["scope"].get("audience_group")
    scopes = [row["platform"], None]  # the experiment's own platform first, then all platforms
    chosen = None
    for plat in scopes:
        cmp = compare_arms(bench, parsed["dimension"], parsed["a"], parsed["b"], platform=plat, audience_group=group, cfg=cfg)
        enough = all(
            arm["campaigns"] >= cfg.min_segment_campaigns and arm["spend"] >= cfg.min_segment_spend
            for arm in (cmp["a"], cmp["b"])
        )
        if enough and cmp["ratio_a_over_b"] is not None:
            chosen = cmp
            break
    if not chosen:
        return {"verdict": "insufficient data", "detail": "Too few settled campaigns on one or both arms."}

    ratio = chosen["ratio_a_over_b"]
    result = str(row["result"]).lower()
    lo, hi = 1 - cfg.observed_margin, 1 + cfg.observed_margin
    if result == "win":
        verdict = "agrees" if ratio >= hi else "disagrees" if ratio <= lo else "unclear"
    elif result == "loss":
        verdict = "agrees" if ratio <= lo else "disagrees" if ratio >= hi else "unclear"
    elif result == "neutral":
        verdict = "agrees" if abs(ratio - 1) <= cfg.neutral_band else "disagrees"
    else:
        verdict = "no claim"
    where = f"on {chosen['scope']['platform']}" if chosen["scope"]["platform"] != "all" else "across all platforms"
    held = f", holding {' and '.join(chosen['held_constant'])} constant" if chosen["held_constant"] else ""
    return {
        "verdict": verdict,
        "ratio_a_over_b": ratio,
        "comparison": chosen,
        "detail": (
            f"{parsed['a']} returns {ratio:.2f}x the pipeline per dollar of {parsed['b']} in settled campaigns {where}"
            + (f" for {group} audiences" if group else "")
            + f"{held} ({chosen['a']['campaigns']} vs {chosen['b']['campaigns']} campaigns)."
        ),
    }


def assess(ds: Dataset, bench: pd.DataFrame, cfg: Config, pack: EvidencePack) -> list[dict]:
    e = ds.experiments.sort_values("experiment_id")
    out: list[dict] = []
    for _, row in e.iterrows():
        parsed = parse_hypothesis(row["hypothesis"], cfg)
        tier, reasons = score(row, cfg)
        out.append(
            {
                "experiment_id": row["experiment_id"],
                "platform": row["platform"],
                "start_date": row["start_date"],
                "variable_tested": row["variable_tested"],
                "hypothesis": row["hypothesis"],
                "theme": row["theme"],
                "logged_result": row["result"],
                "logged_lift_pct": row["lift_pct"],
                "logged_confidence": row["confidence"],
                "runtime_days": int(row["runtime_days"]),
                "sample_size": int(row["sample_size"]),
                "primary_metric": row["primary_metric"],
                "notes": row["notes"],
                "parsed": parsed,
                "comparison_key": comparison_key(row["hypothesis"], parsed),
                "tier": tier,
                "reasons": reasons,
                "usable_as_evidence": tier != "rejected",
                "overturned": tier == "rejected" and str(row["result"]).lower() in ("win", "loss"),
                "observed": observed_check(row, parsed, bench, cfg),
                "replicates": [],
            }
        )

    # Repeats of the same question: a valid repeat strengthens the original.
    by_key: dict[str, list[dict]] = {}
    for a in out:
        by_key.setdefault(a["comparison_key"], []).append(a)
    for group in by_key.values():
        for a in group:
            a["replicates"] = [o["experiment_id"] for o in group if o is not a]

    for a in out:
        if a["tier"] == "rejected":
            statement = (
                f"{a['experiment_id']} ({a['hypothesis']}, {a['platform']}) is logged as {a['logged_result']} "
                f"{a['logged_lift_pct']:+.0f}% but is not a valid read: " + "; ".join(a["reasons"]) + "."
            )
        else:
            statement = (
                f"{a['experiment_id']} ({a['hypothesis']}, {a['platform']}): {a['logged_result']} "
                f"{a['logged_lift_pct']:+.0f}% on {a['primary_metric']} over {a['runtime_days']} days, n={a['sample_size']}. "
                f"Rated {a['tier']}" + (" because " + "; ".join(a["reasons"]) if a["reasons"] else "") + "."
            )
        if a["observed"]["verdict"] in ("agrees", "disagrees"):
            statement += f" Campaign data {a['observed']['verdict']}: {a['observed']['detail']}"
        if a["replicates"]:
            statement += f" Same question as {', '.join(a['replicates'])}."
        pack.add(
            f"EXP.{a['experiment_id']}",
            f"Experiment {a['experiment_id']}: {a['hypothesis']}",
            statement,
            "experiment_history + campaign_summary",
            "final" if a["tier"] == "trusted" else "observational" if a["tier"] == "directional" else "data_quality",
            data=a,
            caveats=(
                ["Rejected experiments may not be cited as support for any recommendation."] if a["tier"] == "rejected" else []
            ),
        )

    tiers = pd.Series([a["tier"] for a in out]).value_counts().to_dict()
    overturned = [a["experiment_id"] for a in out if a["overturned"]]
    contradicted = [a["experiment_id"] for a in out if a["observed"]["verdict"] == "disagrees"]
    pack.add(
        "EXP.summary",
        "How much of the experiment log can be trusted",
        (
            f"Of {len(out)} logged experiments, {tiers.get('trusted', 0)} are trusted, {tiers.get('directional', 0)} are "
            f"directional and {tiers.get('rejected', 0)} are rejected for short runtime or small sample. "
            f"{len(overturned)} logged wins or losses are overturned ({', '.join(overturned) or 'none'}). "
            f"Campaign data disagrees with {', '.join(contradicted) or 'none'}; for a valid test that is a reason "
            f"to re-confirm, not to overturn."
        ),
        "experiment_history + campaign_summary",
        "final",
        data={
            "tiers": tiers,
            "overturned": overturned,
            "contradicted_by_campaign_data": contradicted,
            "rules": {
                "min_runtime_days": cfg.min_runtime_days,
                "min_sample_size": cfg.min_sample_size,
                "outcome_metrics": list(cfg.outcome_metrics),
            },
        },
    )
    return out
