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
from starlette.routing import Route

from .analysis.metrics import to_jsonable
from .approval import ApprovalDesk, DecisionRefused
from .pipeline import ASSUMPTIONS, Result, build

WEB = Path(__file__).parent / "web"


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

    def state() -> dict:
        b = brief()
        cited: set[str] = set()
        if b:
            doc = b["brief"]
            claims = [doc["headline"], *doc["what_happened"], *doc["why"], *doc["creative_recommendations"], *doc["risks_and_observations"]]
            for e in doc["experiments"]:
                claims.append(e["rationale"])
                cited.update(e["proposal"]["evidence_ids"])
            for c in claims:
                cited.update(c["evidence_ids"])
        index = {
            e.id: {"title": e.title, "reliability": e.reliability, "statement": e.statement}
            for e in result.pack.items() if e.id in cited or e.id.startswith("DQ.")
        }
        cfg = result.config
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
                "decisions": desk.latest(),
                "log": desk.log(),
                "staged": desk.staged(),
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
