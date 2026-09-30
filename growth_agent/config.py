"""Every threshold the agent uses lives here, with the reason it was chosen.

Nothing in the analysis or guardrail code hardcodes a number. A marketing lead
can change how conservative the agent is by editing this file, and the change
is visible in one diff.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    # ---- Reporting window -------------------------------------------------
    # "Last week" = the 7 days ending on the latest date in the data, compared
    # with the 7 days before it. Full 7-day windows keep the weekday/weekend
    # pattern (weekend spend runs ~65% of weekday) from distorting the read.
    week_days: int = 7

    # ---- Attribution maturity ---------------------------------------------
    # Fallback lag if the source has no attribution_status field. When the
    # field exists the agent uses it and checks it empirically.
    lead_maturity_days: int = 14
    # Trailing window used as "this campaign's normal" when checking lag.
    baseline_days: int = 28

    # ---- Experiment trust -------------------------------------------------
    # Two full weekly cycles is the floor for any read, and 100 units per test
    # is the floor below which a 10-20% lift cannot be told apart from noise.
    min_runtime_days: int = 14
    min_sample_size: int = 100
    # Metrics that reflect business outcomes. Anything else is a proxy and can
    # never be the primary metric of a trusted test or a new proposal.
    outcome_metrics: tuple[str, ...] = (
        "qualified pipeline per $",
        "pipeline per $",
        "arr per $",
        "opportunity rate",
        "qualified lead rate",
        "cost per opportunity",
    )
    proxy_metrics: tuple[str, ...] = (
        "ctr",
        "cpc",
        "lead conversion rate",
        "registration rate",
        "demo conversion rate",
    )
    # A neutral result is "consistent" with observed data if the two arms are
    # within this band of each other on pipeline per dollar.
    neutral_band: float = 0.20
    # Observed campaign data only 'agrees' or 'disagrees' with a win/loss
    # claim when the arms differ by more than this margin.
    observed_margin: float = 0.10

    # ---- Segment analysis -------------------------------------------------
    # A segment needs this much spend and this many campaigns before the agent
    # will call a difference a finding.
    min_segment_spend: float = 25_000.0
    min_segment_campaigns: int = 3
    # Like-for-like index beyond which a gap becomes a signal. The gap must
    # also point the same way in every platform x offer cell with enough spend.
    gap_index_low: float = 0.80
    gap_index_high: float = 1.20
    # A platform has a lead-quality problem when its qualified-lead rate is
    # below this fraction of the best platform's.
    lead_quality_ratio: float = 0.60
    # Share-of-spend change (percentage points) that counts as a mix shift.
    mix_shift_points: float = 20.0
    recent_weeks: int = 8

    # ---- Creative fatigue -------------------------------------------------
    # Fatigue onset = first week of age where within-campaign CTR falls below
    # this fraction of the campaign's own first-two-week CTR.
    fatigue_index_threshold: float = 0.95
    fatigue_min_campaigns: int = 5
    fatigue_baseline_days: int = 14

    # ---- Guardrails on proposed experiments --------------------------------
    # Pipeline metrics need a longer flight than the experiment-trust floor.
    min_planned_runtime_days: int = 28
    # Below this many expected opportunities per arm a pipeline read is noisy;
    # the agent warns and suggests a nearer-funnel outcome as the decision metric.
    min_expected_opportunities: int = 30
    # Highest daily budget any historical campaign ran at. The agent may not
    # propose more than the team has already been comfortable spending.
    max_daily_budget: float = 1_500.0
    # Ceiling on the total cost of a single staged test. Assumption: set by
    # the marketing lead; 60k is roughly one large historical campaign.
    max_total_test_budget: float = 60_000.0
    # Statuses an agent-created object is allowed to have. "ACTIVE" is absent
    # on purpose: only a human action outside this codebase can launch.
    allowed_staging_statuses: tuple[str, ...] = ("DRAFT", "PAUSED")

    # ---- Label normalization ----------------------------------------------
    audience_aliases: dict[str, str] = field(
        default_factory=lambda: {
            "lf ent": "Law Firm - Enterprise",
            "law firm ent": "Law Firm - Enterprise",
            "law firm mm": "Law Firm - Mid-Market",
            "lf mm": "Law Firm - Mid-Market",
            "ih mm": "In-House - Mid-Market",
            "ih ent": "In-House - Enterprise",
            "enterprise legal": "In-House - Enterprise",
        }
    )

    # ---- Vocabulary used to read "A vs B" experiment hypotheses ------------
    # alias -> (dimension, canonical value). Longest alias wins.
    hypothesis_vocab: dict[str, tuple[str, str]] = field(
        default_factory=lambda: {
            "roi": ("theme", "ROI"),
            "ai productivity": ("theme", "AI Productivity"),
            "productivity": ("theme", "AI Productivity"),
            "speed": ("theme", "Speed"),
            "customer proof": ("theme", "Customer Proof"),
            "security": ("theme", "Security"),
            "workflow automation": ("theme", "Workflow Automation"),
            "workflow": ("theme", "Workflow Automation"),
            "automation": ("theme", "Workflow Automation"),
            "demo": ("objective", "Demo"),
            "webinar": ("objective", "Webinar"),
            "content download": ("objective", "Content Download"),
            "video": ("format", "Video"),
            "static": ("format", "Static"),
            "carousel": ("format", "Carousel"),
            "talk to sales": ("cta", "Talk to Sales"),
            "book demo": ("cta", "Book Demo"),
            "register": ("cta", "Register"),
            "save your seat": ("cta", "Save Your Seat"),
        }
    )


CONFIG = Config()
