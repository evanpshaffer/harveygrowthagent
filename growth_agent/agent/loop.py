"""The agent loop: model proposes, code checks, model repairs, code decides.

The model works through tools. It can read evidence, look at the creative
library and test an experiment design against the guardrails. It finishes by
submitting a structured brief, which is reviewed by code. Problems go back to
the model a bounded number of times. Whatever still fails after that is
removed from the brief and listed as held back, so nothing unverified ships.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from pydantic import ValidationError

from ..analysis.metrics import to_jsonable
from ..guardrails import validate
from ..pipeline import Result
from .claims import check_claim, context_numbers, extract_numbers, mentions_downstream
from .prompt import SYSTEM, TOOLS, build_context
from .schema import Brief, Claim

MAX_TOOL_RESULT_CHARS = 40_000


class ModelClient(Protocol):
    """Anything that can take a messages request and return a normalized reply."""

    model: str
    mode: str

    def create(self, **kwargs) -> dict: ...


class AgentError(RuntimeError):
    pass


@dataclass
class Review:
    brief: Brief | None
    problems: list[dict]                      # [{"where": ..., "message": ...}]
    verdicts: list[dict] = field(default_factory=list)   # guardrail verdict per experiment

    @property
    def accepted(self) -> bool:
        return self.brief is not None and not self.problems


@dataclass
class AgentRun:
    brief: Brief
    verdicts: list[dict]
    held_back: list[dict]
    submit_attempts: int
    turns: int
    trace: list[dict]
    usage: dict
    cost_usd: float | None
    model: str
    mode: str
    seconds: float

    def to_dict(self) -> dict:
        return to_jsonable(
            {
                "brief": self.brief.model_dump(),
                "experiment_verdicts": self.verdicts,
                "held_back": self.held_back,
                "run": {
                    "model": self.model, "mode": self.mode, "turns": self.turns,
                    "submit_attempts": self.submit_attempts, "usage": self.usage,
                    "cost_usd": self.cost_usd, "seconds": round(self.seconds, 1),
                },
                "trace": self.trace,
            }
        )


# --------------------------------------------------------------------------- review

def review(payload: Any, result: Result) -> Review:
    """Check a submitted brief. Code, not the model, decides whether it passes."""
    cfg, pack = result.config, result.pack
    try:
        brief = Brief(**payload) if isinstance(payload, dict) else Brief.model_validate(payload)
    except (ValidationError, TypeError) as err:
        errors = err.errors() if isinstance(err, ValidationError) else [{"loc": ("brief",), "msg": str(err)}]
        return Review(None, [{"where": "schema." + ".".join(map(str, e["loc"])), "message": e["msg"]} for e in errors])

    problems: list[dict] = []
    ctx = context_numbers(cfg, result.windows.as_dict())

    def check(where: str, claim: Claim, extra: set[float] | None = None) -> None:
        for message in check_claim(claim.text, claim.evidence_ids, pack, ctx | (extra or set())):
            problems.append({"where": where, "message": message})

    check("headline", brief.headline)
    for i, c in enumerate(brief.what_happened):
        check(f"what_happened[{i}]", c)
        if mentions_downstream(c.text) and "DQ.attribution_lag" not in c.evidence_ids:
            problems.append({
                "where": f"what_happened[{i}]",
                "message": "mentions qualified leads, opportunities, pipeline or revenue for the reporting week without citing "
                           "DQ.attribution_lag. Those figures are provisional and must be presented that way.",
            })
    for i, c in enumerate(brief.why):
        check(f"why[{i}]", c)
    for i, c in enumerate(brief.creative_recommendations):
        check(f"creative_recommendations[{i}]", c)
        hits = [t for t in cfg.unsupported_assurance_terms if t in c.text.lower()]
        if hits:
            problems.append({
                "where": f"creative_recommendations[{i}]",
                "message": f"contains an assurance the evidence cannot support ({', '.join(hits)}). Recommend direction only.",
            })
    for i, c in enumerate(brief.risks_and_observations):
        check(f"risks_and_observations[{i}]", c)

    verdicts = []
    seen: dict[tuple, int] = {}
    if sorted(e.rank for e in brief.experiments) != [1, 2, 3]:
        problems.append({"where": "experiments", "message": "ranks must be exactly 1, 2 and 3."})
    if len({e.proposal.proposal_id for e in brief.experiments}) != len(brief.experiments):
        problems.append({"where": "experiments", "message": "proposal_id values must be unique."})
    for i, e in enumerate(brief.experiments):
        where = f"experiments[{i}]"
        verdict = validate(e.proposal, result)
        verdicts.append(verdict)
        for b in verdict["blocks"]:
            problems.append({"where": where, "message": f"guardrail '{b['rule']}': {b['message']}"})
        # Three slots, three decisions: the same comparison may not be tested twice.
        for dim in verdict["computed"].get("differs_on", []):
            pair = tuple(sorted(str(getattr(arm, dim, None) or arm.creative_id) for arm in (e.proposal.control, e.proposal.variant)))
            key = (dim, pair)
            if key in seen:
                problems.append({
                    "where": where,
                    "message": f"tests the same comparison as experiments[{seen[key]}] ({dim}: {' vs '.join(pair)}). Use each of the "
                               "three slots for a different decision. If a result should be repeated on a second platform, say so "
                               "in the first test's decision rule.",
                })
            else:
                seen[key] = i
        if e.signal_id and not pack.has(e.signal_id):
            problems.append({"where": where, "message": f"signal_id '{e.signal_id}' does not exist."})
        # Numbers that belong to the design itself are allowed in the experiment's own text.
        design = {float(e.proposal.daily_budget_per_arm), float(e.proposal.runtime_days)}
        design |= {v for _, v, _ in extract_numbers(e.proposal.decision_rule)}
        design |= {float(v) for v in _leaves(verdict["computed"])}
        check(f"{where}.rationale", e.rationale, design)
        free_text = Claim(
            text=" ".join([e.expected_learning, e.proposal.title, e.proposal.hypothesis]),
            evidence_ids=list(dict.fromkeys(e.rationale.evidence_ids + e.proposal.evidence_ids)),
        )
        check(where, free_text, design)
    return Review(brief, problems, verdicts)


def _leaves(node: Any):
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _leaves(v)
    elif isinstance(node, list):
        for v in node:
            yield from _leaves(v)


def finalize(rev: Review, result: Result) -> tuple[Brief, list[dict], list[dict]]:
    """Remove whatever still fails. Returns (brief, verdicts, held_back)."""
    brief = rev.brief
    assert brief is not None
    failing = {p["where"].split(".")[0] if p["where"].startswith("experiments[") else p["where"] for p in rev.problems}
    held: list[dict] = []

    def keep(section: str, items: list) -> list:
        out = []
        for i, item in enumerate(items):
            where = f"{section}[{i}]"
            if where in failing:
                reasons = [p["message"] for p in rev.problems if p["where"].startswith(where)]
                label = item.text if isinstance(item, Claim) else item.proposal.title
                held.append({"where": where, "text": label, "reasons": reasons})
            else:
                out.append(item)
        return out

    data = brief.model_copy(deep=True)
    verdicts = [v for i, v in enumerate(rev.verdicts) if f"experiments[{i}]" not in failing]
    for section in ("what_happened", "why", "creative_recommendations", "risks_and_observations", "experiments"):
        setattr(data, section, keep(section, getattr(brief, section)))
    if "headline" in failing:
        top = result.signals[0]
        held.append({"where": "headline", "text": brief.headline.text, "reasons": [p["message"] for p in rev.problems if p["where"] == "headline"]})
        data.headline = Claim(text=top["statement"], evidence_ids=[top["id"]])
    return data, verdicts, held


# --------------------------------------------------------------------------- loop

def _tool_result(result: Result, name: str, args: dict) -> tuple[Any, bool]:
    """Run a read or validate tool. Returns (payload, is_error)."""
    if name == "get_evidence":
        ids = args.get("ids") or []
        items = [result.pack.get(i).as_dict() if result.pack.has(i) else {"id": i, "error": "unknown evidence id"} for i in ids]
        return items, False
    if name == "list_creatives":
        return to_jsonable(result.dataset.creatives), False
    if name == "validate_experiment":
        return to_jsonable(validate(args.get("proposal") or {}, result)), False
    return {"error": f"unknown tool '{name}'"}, True


def _summarize(name: str, args: dict, payload: Any) -> str:
    if name == "get_evidence":
        return f"read {', '.join(args.get('ids') or [])}"
    if name == "list_creatives":
        return "read the creative library"
    if name == "validate_experiment":
        title = (args.get("proposal") or {}).get("title", "untitled")
        if payload["verdict"] == "blocked":
            return f"'{title}' blocked: " + "; ".join(sorted({b['rule'] for b in payload['blocks']}))
        return f"'{title}' cleared for human review" + (f" with {len(payload['warnings'])} warning(s)" if payload["warnings"] else "")
    return name


def run_agent(result: Result, client: ModelClient, on_event: Callable[[str], None] | None = None) -> AgentRun:
    cfg = result.config
    say = on_event or (lambda _msg: None)
    messages: list[dict] = [{"role": "user", "content": build_context(result)}]
    usage = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    trace: list[dict] = []
    submits = 0
    final: Review | None = None
    started = time.time()
    turn = 0

    for turn in range(1, cfg.max_agent_turns + 1):
        reply = client.create(
            model=client.model, max_tokens=cfg.max_output_tokens, system=SYSTEM, tools=TOOLS, messages=messages
        )
        for k in usage:
            usage[k] += int(reply["usage"].get(k) or 0)
        messages.append({"role": "assistant", "content": reply["raw_content"]})
        calls = [b for b in reply["blocks"] if b.get("type") == "tool_use"]

        if not calls:
            if reply.get("stop_reason") == "max_tokens":
                raise AgentError("The model ran out of output tokens before finishing. Raise max_output_tokens in config.")
            messages.append({"role": "user", "content": "Finish by calling submit_brief with the complete brief."})
            trace.append({"turn": turn, "event": "model replied without a tool call; reminded to submit"})
            continue

        results = []
        for call in calls:
            name, args = call["name"], call.get("input") or {}
            if name == "submit_brief":
                submits += 1
                rev = review(args.get("brief"), result)
                left = cfg.max_submit_attempts - submits
                if rev.accepted:
                    payload, final = {"status": "accepted"}, rev
                    note = f"brief accepted on attempt {submits}"
                else:
                    payload = {"status": "needs_fixes", "attempts_left": left, "problems": rev.problems}
                    note = f"brief returned with {len(rev.problems)} problem(s) on attempt {submits}"
                    if left <= 0 and rev.brief is not None:
                        final = rev
                is_error = False
            else:
                payload, is_error = _tool_result(result, name, args)
                note = _summarize(name, args, payload)
            say(f"  turn {turn}: {note}")
            trace.append({"turn": turn, "tool": name, "event": note})
            text = json.dumps(payload, default=str)
            if len(text) > MAX_TOOL_RESULT_CHARS:
                text = text[:MAX_TOOL_RESULT_CHARS] + '... [truncated: request fewer ids per call]'
            results.append({"type": "tool_result", "tool_use_id": call["id"], "content": text, "is_error": is_error})
        messages.append({"role": "user", "content": results})
        if final is not None:
            break

    if final is None:
        raise AgentError(
            f"The agent did not produce a usable brief within {cfg.max_agent_turns} turns and {submits} submission(s)."
        )

    brief, verdicts, held = finalize(final, result) if final.problems else (final.brief, final.verdicts, [])
    price = cfg.model_prices.get(client.model)
    cost = None
    if price is not None:
        p_in, p_out, read_mult = price
        cost = (
            usage["input_tokens"] * p_in
            + usage["cache_creation_input_tokens"] * p_in * cfg.cache_write_multiplier
            + usage["cache_read_input_tokens"] * p_in * read_mult
            + usage["output_tokens"] * p_out
        ) / 1e6
    return AgentRun(brief, verdicts, held, submits, turn, trace, usage, cost, client.model, client.mode, time.time() - started)


# --------------------------------------------------------------------------- clients

class LiveClient:
    """Calls the Claude API. Reads ANTHROPIC_API_KEY from the environment."""

    mode = "live"

    def __init__(self, model: str, record_to: str | None = None, cache: bool = True):
        import anthropic

        self.model = model
        self._client = anthropic.Anthropic()
        self._record_to = record_to
        self._turns: list[dict] = []
        self._cache = cache

    def _call(self, **kwargs):
        """Call the API with automatic prompt caching, falling back cleanly if it is not available."""
        if self._cache:
            try:
                return self._client.messages.create(cache_control={"type": "ephemeral"}, **kwargs)
            except TypeError:
                self._cache = False   # this SDK version does not know the parameter
            except Exception as err:
                if "cache_control" not in str(err):
                    raise
                self._cache = False   # the API rejected it for this model or account
        return self._client.messages.create(**kwargs)

    def create(self, **kwargs) -> dict:
        resp = self._call(**kwargs)
        blocks = [b.model_dump() for b in resp.content]
        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "cache_creation_input_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0) or 0,
            "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
        }
        if self._record_to:
            keep = [b for b in blocks if b.get("type") in ("text", "tool_use")]
            self._turns.append({"blocks": keep, "stop_reason": resp.stop_reason, "usage": usage})
            with open(self._record_to, "w") as f:
                json.dump({"model": self.model, "recorded": "live run", "turns": self._turns}, f, indent=1, default=str)
        return {"raw_content": resp.content, "blocks": blocks, "stop_reason": resp.stop_reason, "usage": usage}


class ReplayClient:
    """Replays a recorded run turn by turn. No network, no key, no cost."""

    mode = "replay"

    def __init__(self, path: str):
        with open(path) as f:
            data = json.load(f)
        self.model = data.get("model", "recorded")
        self.source = data.get("recorded", "recording")
        self._turns = data["turns"]
        self._i = 0

    def create(self, **_kwargs) -> dict:
        if self._i >= len(self._turns):
            raise AgentError("The recording ended before the brief was accepted.")
        t = self._turns[self._i]
        self._i += 1
        return {"raw_content": t["blocks"], "blocks": t["blocks"], "stop_reason": t.get("stop_reason"), "usage": t.get("usage", {})}
