"""Generate the Weekly Experimentation Brief.

    python -m growth_agent.brief                                   # live run, needs ANTHROPIC_API_KEY
    python -m growth_agent.brief --record examples/recorded_run.json
    python -m growth_agent.brief --replay examples/recorded_run.json   # offline, no key, no cost
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .agent.loop import AgentError, LiveClient, ReplayClient, run_agent
from .agent.render import render_brief
from .config import CONFIG
from .pipeline import build
from .report import render


def load_dotenv(path: str = ".env") -> None:
    """Read KEY=VALUE lines from a local .env file, without overriding the real environment."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Growth Agent: write the Weekly Experimentation Brief")
    ap.add_argument("--source", default="csv")
    ap.add_argument("--out", default="out")
    ap.add_argument("--model", default=os.environ.get("GROWTH_AGENT_MODEL", CONFIG.default_model))
    ap.add_argument("--replay", default=None, help="replay a recorded run instead of calling the API")
    ap.add_argument("--record", default=None, help="save the live run's model turns to this file")
    args = ap.parse_args()
    load_dotenv()

    print("1/3 Analysis engine: loading data and computing evidence")
    result = build(source=args.source)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "evidence_pack.json").write_text(json.dumps(result.to_dict(), indent=2))
    (out / "analysis_report.md").write_text(render(result))
    print(f"    {len(result.pack.ids())} evidence items, {len(result.signals)} signals")

    if args.replay:
        client = ReplayClient(args.replay)
        print(f"2/3 Reasoning layer: replaying {args.replay} (no API call)")
    else:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit(
                "ANTHROPIC_API_KEY is not set.\n"
                "  Put it in a .env file in this folder:  ANTHROPIC_API_KEY=sk-ant-...\n"
                "  or run:  export ANTHROPIC_API_KEY=sk-ant-...\n"
                "  To run without a key:  python -m growth_agent.brief --replay examples/recorded_run.json"
            )
        client = LiveClient(args.model, record_to=args.record)
        print(f"2/3 Reasoning layer: {args.model} is reading evidence and designing experiments")

    try:
        run = run_agent(result, client, on_event=print)
    except AgentError as err:
        sys.exit(f"Agent stopped: {err}")
    except Exception as err:  # API problems: bad key, no credits, network, model name
        if type(err).__module__.startswith("anthropic"):
            sys.exit(
                f"The Claude API call failed ({type(err).__name__}): {err}\n"
                "  Check the key in .env, that the Console account has credits, and the model name "
                f"('{args.model}').\n  Nothing was written to {out / 'brief.md'}."
            )
        raise

    print("3/3 Checks: every number matched to evidence, every experiment through the guardrails")
    (out / "brief.json").write_text(json.dumps(run.to_dict(), indent=2))
    (out / "brief.md").write_text(render_brief(run, result))
    print(f"    {len(run.brief.experiments)} experiments ready for human review, {len(run.held_back)} item(s) held back")
    if run.mode == "live" and run.cost_usd is not None:
        print(f"    {run.usage['input_tokens']:,} input + {run.usage['output_tokens']:,} output tokens, ${run.cost_usd:.2f}, {run.seconds:.0f}s")
    print(f"Wrote {out / 'brief.md'} and {out / 'brief.json'}")
    print("Nothing was launched. The experiments are drafts awaiting approval.")


if __name__ == "__main__":
    main()
