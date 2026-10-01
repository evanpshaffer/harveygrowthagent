"""The human checkpoint.

Every decision a reviewer makes is appended to a log that is never rewritten.
An experiment's state is whatever its latest log entry says. Staging reads
this log: no approval entry for the exact design, no draft.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .guardrails import validate
from .pipeline import Result
from .staging import StagingRefused, build_draft, proposal_hash

EDITABLE = ("daily_budget_per_arm", "runtime_days")   # what a reviewer can change without redesigning the test


class DecisionRefused(ValueError):
    """The reviewer asked for something the guardrails or the process do not allow."""

    def __init__(self, message: str, blocks: list[dict] | None = None):
        super().__init__(message)
        self.blocks = blocks or []


class ApprovalDesk:
    def __init__(self, result: Result, out_dir: str | Path = "out"):
        self.result = result
        self.out = Path(out_dir)
        self.log_path = self.out / "approvals.jsonl"
        self.staged_dir = self.out / "staged"

    # ---- reading -------------------------------------------------------------
    def log(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        return [json.loads(line) for line in self.log_path.read_text().splitlines() if line.strip()]

    def latest(self) -> dict[str, dict]:
        """Current decision per experiment: the last entry wins."""
        state: dict[str, dict] = {}
        for entry in self.log():
            state[entry["proposal_id"]] = entry
        return state

    def current(self, proposals: list[dict]) -> dict[str, dict]:
        """Decisions that still apply to the designs in front of the reviewer.

        A decision is tied to the fingerprint of the design it was made on. If a
        new brief proposes a different design under the same id, the old decision
        stays in the log but no longer counts, and the experiment is pending again.
        """
        live: dict[str, dict] = {}
        latest = self.latest()
        for p in proposals:
            entry = latest.get(p["proposal_id"])
            if not entry:
                continue
            edits = {k: v["to"] for k, v in (entry.get("edits") or {}).items()}
            if entry["proposal_hash"] == proposal_hash(self.apply_edits(p, edits)):
                live[p["proposal_id"]] = entry
        return live

    def staged(self) -> dict[str, dict]:
        if not self.staged_dir.exists():
            return {}
        return {p.stem: json.loads(p.read_text()) for p in sorted(self.staged_dir.glob("*.json"))}

    # ---- deciding ------------------------------------------------------------
    @staticmethod
    def apply_edits(proposal: dict, edits: dict | None) -> dict:
        edited = json.loads(json.dumps(proposal))
        for key, value in (edits or {}).items():
            if key not in EDITABLE:
                raise DecisionRefused(f"'{key}' cannot be edited here. Budget and runtime can; anything else is a new design.")
            edited[key] = type(proposal[key])(value)
        return edited

    def preview(self, proposal: dict, edits: dict | None) -> dict:
        """What the guardrails say about an edited design, before anyone commits to it."""
        return validate(self.apply_edits(proposal, edits), self.result)

    def decide(self, proposal: dict, decision: str, reviewer: str, note: str = "", edits: dict | None = None) -> dict:
        """Record a reviewer's decision. Approving also stages the paused draft."""
        reviewer = (reviewer or "").strip()
        if not reviewer:
            raise DecisionRefused("A decision needs a named reviewer.")
        if decision not in ("approved", "rejected", "reopened"):
            raise DecisionRefused(f"Unknown decision '{decision}'.")

        changed = {k: v for k, v in (edits or {}).items() if str(v) != str(proposal.get(k))}
        final = self.apply_edits(proposal, changed)
        entry = {
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "proposal_id": proposal["proposal_id"],
            "title": proposal["title"],
            "decision": decision,
            "reviewer": reviewer,
            "note": note.strip(),
            "edits": {k: {"from": proposal[k], "to": final[k]} for k in changed},
            "proposal_hash": proposal_hash(final),
        }

        if decision == "approved":
            verdict = validate(final, self.result)
            if verdict["verdict"] != "ready_for_human_review":
                raise DecisionRefused("The guardrails block this design, so it cannot be approved.", verdict["blocks"])
            # The ceiling on the three tests together holds at approval time too.
            others = sum(d["experiment"]["total_budget_usd"] for pid, d in self.staged().items() if pid != proposal["proposal_id"])
            cap = self.result.config.max_slate_budget
            if others + verdict["computed"]["total_budget"] > cap:
                raise DecisionRefused(
                    f"Approving this would bring approved tests to ${others + verdict['computed']['total_budget']:,.0f}, "
                    f"over the ${cap:,.0f} ceiling for one brief. Lower this budget or reopen another test."
                )
            self._append(entry)
            self._stage(final, verdict)
        else:
            self._append(entry)
            self._unstage(proposal["proposal_id"])
        return entry

    # ---- staging ---------------------------------------------------------------
    def _stage(self, proposal: dict, verdict: dict) -> dict:
        """Write the paused draft. Only reachable through a recorded approval of this exact design."""
        approval = self.latest().get(proposal["proposal_id"])
        if not approval or approval["decision"] != "approved":
            raise StagingRefused("No approval on record for this experiment.")
        if approval["proposal_hash"] != proposal_hash(proposal):
            raise StagingRefused("The design changed after it was approved. It needs a new approval.")
        draft = build_draft(proposal, verdict, approval, self.result.config)
        self.staged_dir.mkdir(parents=True, exist_ok=True)
        (self.staged_dir / f"{proposal['proposal_id']}.json").write_text(json.dumps(draft, indent=2))
        return draft

    def stage(self, proposal: dict) -> dict:
        """Public entry point for staging. Re-validates, then requires the approval."""
        verdict = validate(proposal, self.result)
        if verdict["verdict"] != "ready_for_human_review":
            raise StagingRefused("The guardrails block this design.")
        return self._stage(proposal, verdict)

    def _unstage(self, proposal_id: str) -> None:
        path = self.staged_dir / f"{proposal_id}.json"
        if path.exists():
            path.unlink()

    def _append(self, entry: dict) -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
