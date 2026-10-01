"""The approval screen: a local web page for reviewing the brief and deciding on each experiment.

    python -m growth_agent.app          # then open http://localhost:8000

Reads out/brief.json (written by `python -m growth_agent.brief`). Decisions are
appended to out/approvals.jsonl. Approving an experiment writes its paused
launch draft to out/staged/.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from .analysis.metrics import to_jsonable
from .approval import ApprovalDesk, DecisionRefused
from .pipeline import ASSUMPTIONS, Result, build

WEB = Path(__file__).parent / "web"

# Evidence the page's stat tiles and charts are drawn from. Every figure on the
# screen comes out of the evidence pack; the page computes nothing itself.
OVERVIEW_EVIDENCE = ("WEEK.totals", "WEEK.program_status", "DQ.attribution_lag", "MIX.objective", "SEG.platform_objective")


def overview(result: Result) -> dict:
    """Headline figures and chart series, read straight from the evidence pack."""
    pack = result.pack
    week = pack.get("WEEK.totals").data
    status = pack.get("WEEK.program_status").data
    lag = pack.get("DQ.attribution_lag").data
    mix = pack.get("MIX.objective").data
    shifts = mix["shifts"]
    platform = shifts.loc[shifts["change_points"].abs().idxmax(), "platform"]   # where the offer mix moved most
    monthly = mix["monthly_share_pct"]
    cells = pack.get("SEG.platform_objective").data
    return {
        "spend": week["spend"],
        "conversions": week["conversions"],
        "campaigns": week["campaigns"],
        "weekly_spend": [{"week_end": w["week_end"], "spend": w["spend"]} for w in status["weekly_spend"]],
        "peak_week": status["peak_week"],
        "live_on_as_of": len(status["live_on_as_of"]),
        "scheduled_after": len(status["scheduled_after_as_of"]),
        "ql_completeness": lag["ql_completeness"],
        "mix_platform": platform,
        "mix_by_month": monthly[monthly["platform"] == platform].drop(columns="platform").to_dict("records"),
        "offer_efficiency": cells[["platform", "objective", "pipeline_per_dollar", "spend"]].to_dict("records"),
    }


def create_app(out_dir: str = "out", source: str = "csv") -> Starlette:
    result: Result = build(source=source)
    out = Path(out_dir)
    desk = ApprovalDesk(result, out)

    def brief() -> dict | None:
        path = out / "brief.json"
        return json.loads(path.read_text()) if path.exists() else None

    def find(proposal_id: str) -> dict | None:
        b = brief()
        if not b:
            return None
        return next((e["proposal"] for e in b["brief"]["experiments"] if e["proposal"]["proposal_id"] == proposal_id), None)

    def headline_numbers() -> list[dict]:
        """Stat tiles for the top of the page. Each one points at the evidence it came from."""
        week = result.pack.get("WEEK.totals").data
        status = result.pack.get("WEEK.program_status").data
        return [
            {"label": "Spend last week", "value": week["spend"]["this_week"], "format": "money",
             "change_pct": week["spend"]["change_pct"], "note": "vs the week before", "evidence": "WEEK.totals"},
            {"label": "Campaigns live", "value": week["campaigns"]["this_week"], "format": "count",
             "note": f"{week['campaigns']['prior_week']} the week before", "evidence": "WEEK.spend_bridge"},
            {"label": "Conversions", "value": week["conversions"]["this_week"], "format": "count",
             "change_pct": week["conversions"]["change_pct"], "note": "vs the week before", "evidence": "WEEK.totals"},
            {"label": "Scheduled to keep running", "value": len(status["scheduled_after_as_of"]), "format": "count",
             "note": f"of {len(status['live_on_as_of'])} live on the last day", "evidence": "WEEK.program_status"},
        ]

    def charts() -> dict:
        """Data for the two charts, taken straight from the evidence pack."""
        mix = result.pack.get("MIX.objective").data
        shifts = mix["shifts"]
        platform = shifts.loc[shifts["change_points"].abs().idxmax(), "platform"]
        monthly = mix["monthly_share_pct"]
        monthly = monthly[monthly["platform"] == platform].sort_values("month")
        offers = [c for c in monthly.columns if c not in ("platform", "month")]
        po = result.pack.get("SEG.platform_objective").data
        return {
            "offer_mix": {
                "evidence": "MIX.objective", "platform": platform, "months": monthly["month"].tolist(),
                "series": {o: monthly[o].round(1).tolist() for o in offers},
            },
            "pipeline_per_dollar": {
                "evidence": "SEG.platform_objective",
                "platforms": sorted(po["platform"].unique().tolist()),
                "values": {p: {r.objective: r.pipeline_per_dollar for r in po[po["platform"] == p].itertuples()} for p in po["platform"].unique()},
            },
        }

    def state() -> dict:
        b = brief()
        cited: set[str] = {"WEEK.totals", "WEEK.spend_bridge", "WEEK.program_status", "MIX.objective", "SEG.platform_objective"}
        if b:
            doc = b["brief"]
            claims = [doc["headline"], *doc["what_happened"], *doc["why"], *doc["creative_recommendations"], *doc["risks_and_observations"]]
            for e in doc["experiments"]:
                claims.append(e["rationale"])
                cited.update(e["proposal"]["evidence_ids"])
            for c in claims:
                cited.update(c["evidence_ids"])
        cited.update(OVERVIEW_EVIDENCE)
        index = {
            e.id: {"title": e.title, "reliability": e.reliability, "statement": e.statement}
            for e in result.pack.items() if e.id in cited or e.id.startswith("DQ.")
        }
        cfg = result.config
        proposals = [e["proposal"] for e in b["brief"]["experiments"]] if b else []
        decisions = desk.current(proposals)
        approved = {pid for pid, d in decisions.items() if d["decision"] == "approved"}
        return to_jsonable(
            {
                "has_brief": b is not None,
                "brief": b,
                "windows": result.windows.as_dict(),
                "synthetic": result.dataset.is_synthetic,
                "source": result.dataset.source_name,
                "assumptions": ASSUMPTIONS,
                "data_limits": [i for i in ("DQ.attribution_lag", "DQ.reconciliation", "DQ.daily_outcome_gaps")],
                "evidence": index,
                "kpis": headline_numbers(),
                "charts": charts(),
                "overview": overview(result),
                "decisions": decisions,
                "log": desk.log(),
                "staged": {pid: d for pid, d in desk.staged().items() if pid in approved},
                "limits": {
                    "max_daily_budget": cfg.max_daily_budget,
                    "max_total_test_budget": cfg.max_total_test_budget,
                    "max_slate_budget": cfg.max_slate_budget,
                    "min_runtime_days": cfg.min_planned_runtime_days,
                    "attribution_days": cfg.lead_maturity_days,
                },
            }
        )

    async def page(_request: Request) -> HTMLResponse:
        return HTMLResponse((WEB / "index.html").read_text())

    async def get_state(_request: Request) -> JSONResponse:
        return JSONResponse(state())

    async def get_evidence(request: Request) -> JSONResponse:
        eid = request.path_params["eid"]
        if not result.pack.has(eid):
            return JSONResponse({"error": f"No evidence item '{eid}'."}, status_code=404)
        return JSONResponse(result.pack.get(eid).as_dict())

    async def post_preview(request: Request) -> JSONResponse:
        body = await request.json()
        proposal = find(body.get("proposal_id", ""))
        if proposal is None:
            return JSONResponse({"error": "Unknown experiment."}, status_code=404)
        try:
            return JSONResponse(to_jsonable(desk.preview(proposal, body.get("edits"))))
        except (DecisionRefused, ValueError) as err:
            return JSONResponse({"error": str(err)}, status_code=400)

    async def post_decision(request: Request) -> JSONResponse:
        body = await request.json()
        proposal = find(body.get("proposal_id", ""))
        if proposal is None:
            return JSONResponse({"error": "Unknown experiment."}, status_code=404)
        try:
            desk.decide(proposal, body.get("decision", ""), body.get("reviewer", ""), body.get("note", ""), body.get("edits"))
        except DecisionRefused as err:
            return JSONResponse({"error": str(err), "blocks": err.blocks}, status_code=400)
        except ValueError as err:
            return JSONResponse({"error": str(err)}, status_code=400)
        return JSONResponse(state())

    return Starlette(
        routes=[
            Route("/", page),
            Route("/api/state", get_state),
            Route("/api/evidence/{eid}", get_evidence),
            Route("/api/preview", post_preview, methods=["POST"]),
            Route("/api/decisions", post_decision, methods=["POST"]),
            Mount("/fonts", StaticFiles(directory=WEB / "fonts"), name="fonts"),
        ]
    )


def main() -> None:
    import uvicorn

    ap = argparse.ArgumentParser(description="Growth Agent: approval screen")
    ap.add_argument("--out", default="out")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    print(f"Approval screen: http://localhost:{args.port}   (Ctrl+C to stop)")
    uvicorn.run(create_app(args.out), host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
