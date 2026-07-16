"""Small, dependency-free types shared by the Stage 3 evaluation harness."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolExpectation:
    """A required call, with exact or substring checks for selected arguments."""

    name: str
    exact_args: dict[str, Any] = field(default_factory=dict)
    contains_args: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvalCase:
    id: str
    prompt: str
    required_tools: tuple[ToolExpectation, ...] = ()
    forbidden_tools: tuple[str, ...] = ()
    preferred_sequence: tuple[str, ...] = ()
    max_tool_calls: int = 3
    reference_facts: tuple[str, ...] = ()
    tone: str = "professional, calm, and helpful"


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class RunRecord:
    case_id: str
    answer: str
    tool_calls: tuple[ToolCall, ...]


@dataclass(frozen=True)
class Score:
    passed: bool
    score: float
    reasons: tuple[str, ...]
