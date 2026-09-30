"""Command line entry point.

    python -m growth_agent.run                      # build the evidence pack and report
    python -m growth_agent.run --validate proposal.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .guardrails import validate
from .pipeline import build
from .report import render


def main() -> None:
    ap = argparse.ArgumentParser(description="Growth Agent: deterministic analysis and guardrails")
    ap.add_argument("--source", default="csv", help="data source: csv (sample data) or live (not implemented)")
    ap.add_argument("--out", default="out", help="output directory")
    ap.add_argument("--validate", default=None, help="path to a proposed experiment (JSON) to check against the guardrails")
    args = ap.parse_args()

    result = build(source=args.source)

    if args.validate:
        proposal = json.loads(Path(args.validate).read_text())
        print(json.dumps(validate(proposal, result), indent=2, default=str))
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "evidence_pack.json").write_text(json.dumps(result.to_dict(), indent=2))
    (out / "analysis_report.md").write_text(render(result))

    w = result.windows.as_dict()
    tiers = result.pack.get("EXP.summary").data["tiers"]
    print(f"Source            {result.dataset.source_name}{' (synthetic)' if result.dataset.is_synthetic else ''}")
    print(f"Reporting week    {w['reporting_week'][0]} to {w['reporting_week'][1]}")
    print(f"Immature from     {w['immature_from']} ({w['immature_basis']})")
    print(f"Evidence items    {len(result.pack.ids())}")
    print(f"Experiments       {tiers.get('trusted', 0)} trusted, {tiers.get('directional', 0)} directional, {tiers.get('rejected', 0)} rejected")
    print(f"Signals           {len(result.signals)}")
    for s in result.signals[:5]:
        print(f"  {s['rank']}. {s['title']}")
    print(f"Wrote             {out / 'evidence_pack.json'}, {out / 'analysis_report.md'}")


if __name__ == "__main__":
    main()
