"""Domain models shared by the support-agent evaluation suite."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolCallExpectation:
    """A required call, with exact or substring checks for selected arguments."""

    name: str
    exact_args: dict[str, Any] = field(default_factory=dict)
    contains_args: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    prompt: str
    required_tools: tuple[ToolCallExpectation, ...] = ()
    forbidden_tools: tuple[str, ...] = ()
    preferred_sequence: tuple[str, ...] = ()
    max_tool_calls: int = 3
    reference_facts: tuple[str, ...] = ()
    tone: str = "professional, calm, and helpful"


@dataclass(frozen=True)
class ObservedToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class EvaluationRun:
    case_id: str
    answer: str
    tool_calls: tuple[ObservedToolCall, ...]


@dataclass(frozen=True)
class ScoreResult:
    passed: bool
    score: float
    reasons: tuple[str, ...]
