"""Run the Stage 3 golden set against the live support agent.

Usage:
    .venv/bin/python -m evals.run
    .venv/bin/python -m evals.run --judge ollama --case kb_refund_policy
"""

import argparse
import json
from collections.abc import Iterable

from evals.dataset import GOLDEN_CASES
from evals.judge import OllamaJudge
from evals.scorers import deterministic_score, trajectory_score
from evals.types import EvalCase, RunRecord, Score, ToolCall
from support_agent import build_agent, reset_demo_state


def capture_run(case: EvalCase) -> RunRecord:
    """Run a fresh agent and extract its tool-use blocks as the trajectory."""
    reset_demo_state()
    agent = build_agent()
    answer = str(agent(case.prompt))
    calls: list[ToolCall] = []
    for message in agent.messages:
        for block in message.get("content", []):
            if "toolUse" in block:
                tool_use = block["toolUse"]
                calls.append(ToolCall(tool_use["name"], dict(tool_use.get("input", {}))))
    return RunRecord(case.id, answer, tuple(calls))


def _summary(scores: Iterable[Score]) -> dict[str, object]:
    score_list = list(scores)
    passed = sum(score.passed for score in score_list)
    return {"passed": passed, "total": len(score_list), "pass_rate": round(passed / len(score_list), 3) if score_list else 0.0}


def evaluate(cases: Iterable[EvalCase], judge: OllamaJudge | None = None) -> dict[str, object]:
    """Return a JSON-serialisable report; the caller chooses where to persist it."""
    rows = []
    for case in cases:
        run = capture_run(case)
        deterministic = deterministic_score(case, run)
        trajectory = trajectory_score(case, run)
        judge_score = judge.score(case, run) if judge else None
        rows.append({
            "id": case.id,
            "answer": run.answer,
            "tool_calls": [{"name": call.name, "arguments": call.arguments} for call in run.tool_calls],
            "deterministic": {"passed": deterministic.passed, "score": deterministic.score, "reasons": deterministic.reasons},
            "trajectory": {"passed": trajectory.passed, "score": trajectory.score, "reasons": trajectory.reasons},
            "judge": None if judge_score is None else {"passed": judge_score.passed, "score": judge_score.score, "reasons": judge_score.reasons},
        })
    report: dict[str, object] = {
        "cases": rows,
        "deterministic": _summary(Score(row["deterministic"]["passed"], row["deterministic"]["score"], tuple(row["deterministic"]["reasons"])) for row in rows),
        "trajectory": _summary(Score(row["trajectory"]["passed"], row["trajectory"]["score"], tuple(row["trajectory"]["reasons"])) for row in rows),
    }
    if judge:
        report["judge"] = _summary(Score(row["judge"]["passed"], row["judge"]["score"], tuple(row["judge"]["reasons"])) for row in rows)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate support-agent trajectories against the golden set.")
    parser.add_argument("--case", action="append", help="Golden case ID to run; may be repeated.")
    parser.add_argument("--judge", choices=("off", "ollama"), default="off", help="Run the qualitative Ollama judge.")
    parser.add_argument("--output", help="Write the full JSON report to this file.")
    args = parser.parse_args()
    selected = tuple(case for case in GOLDEN_CASES if not args.case or case.id in args.case)
    unknown = set(args.case or ()) - {case.id for case in selected}
    if unknown:
        parser.error(f"unknown case ID(s): {', '.join(sorted(unknown))}")
    report = evaluate(selected, OllamaJudge() if args.judge == "ollama" else None)
    rendered = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w") as file:
            file.write(rendered + "\n")
    print(rendered)
    # A non-zero exit makes this directly usable by the Stage 4 CI gate.
    summaries = [report["deterministic"], report["trajectory"]]
    if "judge" in report:
        summaries.append(report["judge"])
    return 0 if all(summary["passed"] == summary["total"] for summary in summaries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
