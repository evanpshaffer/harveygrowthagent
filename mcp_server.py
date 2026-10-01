"""MCP server: the integration layer exposed as tools.

Any MCP client (Claude Code, Claude Desktop, an agent framework) can connect
and work with the same canonical data, evidence and guardrails the pipeline
uses. The data source is chosen by the GROWTH_AGENT_SOURCE environment
variable, so moving from sample files to live systems does not change a
single tool signature.

Run:  python mcp_server.py
There is deliberately no tool that launches a campaign or spends budget.
"""
from __future__ import annotations

import os
from functools import lru_cache

try:                                              # mcp 2.x renamed FastMCP to MCPServer
    from mcp.server import MCPServer as _Server
except ImportError:                               # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from growth_agent.analysis.metrics import to_jsonable
from growth_agent.guardrails import validate
from growth_agent.pipeline import ASSUMPTIONS, Result, build

mcp = _Server("growth-agent")
MAX_ROWS = 500


@lru_cache(maxsize=1)
def _result() -> Result:
    return build(source=os.environ.get("GROWTH_AGENT_SOURCE", "csv"))


def _filter(df, **filters):
    for col, val in filters.items():
        if val is not None:
            df = df[df[col] == val]
    return df


@mcp.tool()
def get_campaigns(platform: str | None = None, objective: str | None = None, theme: str | None = None, audience: str | None = None) -> list[dict]:
    """Campaign-level lifetime results (the CRM-reconciled record). Use for efficiency questions."""
    df = _filter(_result().dataset.campaigns, platform=platform, objective=objective, theme=theme, audience=audience)
    return to_jsonable(df)


@mcp.tool()
def get_daily_performance(start_date: str, end_date: str, campaign_id: str | None = None, platform: str | None = None) -> dict:
    """Daily delivery and outcomes for a date range. Outcome columns are a partial view; see DQ.reconciliation."""
    d = _result().dataset.daily
    df = _filter(d[(d["date"] >= start_date) & (d["date"] <= end_date)], campaign_id=campaign_id, platform=platform)
    return {"rows": to_jsonable(df.head(MAX_ROWS)), "total_rows": len(df), "truncated": len(df) > MAX_ROWS}


@mcp.tool()
def get_experiments(tier: str | None = None) -> list[dict]:
    """Historical experiments with the agent's trust rating (trusted, directional, rejected) and reasons."""
    exps = _result().experiments
    return to_jsonable([e for e in exps if tier is None or e["tier"] == tier])


@mcp.tool()
def get_creatives() -> list[dict]:
    """The creative library (metadata only)."""
    return to_jsonable(_result().dataset.creatives)


@mcp.tool()
def list_evidence() -> list[dict]:
    """Index of every evidence item: id, title, reliability and its one-sentence statement."""
    return [{"id": e.id, "title": e.title, "reliability": e.reliability, "statement": e.statement} for e in _result().pack.items()]


@mcp.tool()
def get_evidence(ids: list[str]) -> list[dict]:
    """Full evidence items, including the underlying data tables and caveats, for the given ids."""
    pack = _result().pack
    return [pack.get(i).as_dict() if pack.has(i) else {"id": i, "error": "unknown evidence id"} for i in ids]


@mcp.tool()
def get_signals() -> list[dict]:
    """Ranked opportunity signals: where a test would pay off, with evidence ids and cautions."""
    return _result().to_dict()["signals"]


@mcp.tool()
def get_context() -> dict:
    """Reporting window, attribution lag window, stated assumptions and data-quality findings."""
    r = _result()
    return {
        "windows": r.windows.as_dict(),
        "synthetic_data": r.dataset.is_synthetic,
        "assumptions": ASSUMPTIONS,
        "data_quality": [e.as_dict() for e in r.pack.items() if e.id.startswith("DQ.")],
    }


@mcp.tool()
def validate_experiment_proposal(proposal: dict) -> dict:
    """Run a proposed experiment through the guardrails. Best verdict is 'ready_for_human_review'; nothing here can approve or launch."""
    return to_jsonable(validate(proposal, _result()))


if __name__ == "__main__":
    mcp.run()
