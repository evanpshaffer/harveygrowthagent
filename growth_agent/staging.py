"""Closing the loop: prepare an approved experiment for launch, without launching it.

A staged draft is a paused, platform-shaped description of the two campaigns
that make up a test. In this prototype, staging writes that draft to a file.
With live credentials, the same draft would be sent to the ad platform's
create call with a paused status, and a person would still press the button
that makes it spend.

Two things are true by construction:
- stage() refuses to run without a recorded human approval of this exact design.
- no draft can carry a status that spends money.
"""
from __future__ import annotations

import hashlib
import json
import re

from .config import Config
from .guardrails import ExperimentProposal

# How each platform names a campaign that exists but is not spending, and the
# prefix the team's naming convention uses for it.
PLATFORMS = {
    "Google": {"prefix": "GO", "paused_status": "PAUSED", "system": "Google Ads"},
    "LinkedIn": {"prefix": "LI", "paused_status": "DRAFT", "system": "LinkedIn Campaign Manager"},
    "Meta": {"prefix": "ME", "paused_status": "PAUSED", "system": "Meta Ads Manager"},
}


class StagingRefused(RuntimeError):
    """Raised when something tries to stage a test that a person has not approved."""


def proposal_hash(proposal: dict) -> str:
    """Fingerprint of a design. An approval applies to one fingerprint only."""
    body = json.dumps(proposal, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def _campaign_name(prefix: str, p: ExperimentProposal, arm, suffix: str) -> str:
    """Follow the naming convention already used in the account."""
    audience = p.audience.replace(" ", "_")
    parts = [prefix, p.region, audience, (arm.theme or "Theme").replace(" ", "_"), (arm.objective or "Offer").replace(" ", "_"), suffix]
    return re.sub(r"_+", "_", "_".join(parts))


def build_draft(proposal: dict, verdict: dict, approval: dict, cfg: Config) -> dict:
    """The launch draft for an approved experiment. Pure function, no side effects."""
    p = ExperimentProposal.model_validate(proposal)
    platform = PLATFORMS[p.platform]
    status = platform["paused_status"]
    if status not in cfg.allowed_staging_statuses:
        raise StagingRefused(f"Status '{status}' is not an allowed staging status.")

    campaigns = []
    for letter, arm in (("A", p.control), ("B", p.variant)):
        name = _campaign_name(platform["prefix"], p, arm, f"{p.proposal_id}_{letter}")
        campaigns.append(
            {
                "arm": arm.label,
                "role": "control" if letter == "A" else "variant",
                "campaign_name": name,
                "status": status,
                "daily_budget_usd": p.daily_budget_per_arm,
                "flight_days": p.runtime_days,
                "start": "set by the person who activates it",
                "region": p.region,
                "audience": p.audience,
                "targeting": arm.targeting or "account default for this audience",
                "offer": arm.objective,
                "message_theme": arm.theme,
                "cta": arm.cta,
                "creative_id": arm.creative_id,
                "tracking": {"utm_campaign": name.lower(), "utm_content": f"{p.proposal_id}-{letter}".lower()},
            }
        )

    return {
        "draft_for": platform["system"],
        "what_this_is": (
            "A paused draft prepared by the Growth Agent. Field names are the agent's own; a live connector "
            "maps them to the platform's create call. Nothing has been sent to any ad platform."
        ),
        "status": status,
        "spends_money": False,
        "to_launch": f"A person activates both campaigns in {platform['system']}. The agent has no credentials and no activate call.",
        "experiment": {
            "id": p.proposal_id,
            "title": p.title,
            "hypothesis": p.hypothesis,
            "split": "50/50, two campaigns with equal budgets",
            "primary_metric": p.primary_metric,
            "guardrail_metrics": p.guardrail_metrics,
            "decision_rule": p.decision_rule,
            "earliest_valid_read_day": verdict["computed"].get("earliest_readout_day"),
            "total_budget_usd": verdict["computed"].get("total_budget"),
            "evidence_ids": p.evidence_ids,
            "retest_of": p.retest_of,
        },
        "campaigns": campaigns,
        "guardrails": {"verdict": verdict["verdict"], "warnings": [w["message"] for w in verdict["warnings"]]},
        "approval": {
            "approved_by": approval["reviewer"],
            "approved_at": approval["at"],
            "note": approval.get("note") or "",
            "design_fingerprint": approval["proposal_hash"],
            "edited_before_approval": approval.get("edits") or {},
        },
    }
