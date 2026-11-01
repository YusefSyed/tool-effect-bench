"""Per-sample execution context, kept in Inspect's sample Store.

One set of tool definitions serves every sample. Everything the tools, the
approver and the scorer need to know about the running sample (its approval
policy, note placement, note text and scripted faults) lives in the Store under
a ``teb:`` prefix, so parallel samples never share state and the Inspect log
records every change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from inspect_ai.util import store

PREFIX = "teb:"
POLICIES = ("enforce", "allow_protected", "modify")
# v0.2 crosses its notes with these two; v0.3 adds three more (V03-PROTOCOL.md).
V2_PLACEMENTS = ("artifact_note", "tool_error")
PLACEMENTS = (*V2_PLACEMENTS, "result_field", "multi_step", "adaptive")


def get(name: str, default: Any = None) -> Any:
    """Read a prefixed key from the current sample's Store."""
    return store().get(PREFIX + name, default)


def put(name: str, value: Any) -> None:
    """Write a prefixed key to the current sample's Store."""
    store().set(PREFIX + name, value)


@dataclass(frozen=True)
class SampleContext:
    """Trusted, harness-set facts about the running sample."""

    sample_id: str
    policy: str = "enforce"
    placement: str | None = None
    note: str | None = None
    premise: str | None = None
    faults: dict[str, str] = field(default_factory=dict)
    response_override: str | None = None

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise ValueError("unknown trusted approval policy")
        if self.placement is not None and self.placement not in PLACEMENTS:
            raise ValueError("unknown note placement")

    @classmethod
    def from_metadata(cls, sample_id: str, metadata: dict[str, Any]) -> SampleContext:
        """Build the context from sample metadata written by the dataset."""
        return cls(
            sample_id=sample_id,
            policy=str(metadata.get("policy", "enforce")),
            placement=metadata.get("placement"),
            note=metadata.get("note"),
            premise=metadata.get("premise"),
            faults=dict(metadata.get("faults", {})),
            response_override=metadata.get("tool_response_override"),
        )

    @classmethod
    def current(cls) -> SampleContext:
        """Read the installed context for the running sample."""
        sample_id = get("sample_id")
        if not isinstance(sample_id, str):
            raise RuntimeError("sample context not installed")
        return cls(
            sample_id=sample_id,
            policy=str(get("policy", "enforce")),
            placement=get("placement"),
            note=get("note"),
            premise=get("premise"),
            faults=dict(get("faults", {})),
            response_override=get("response_override"),
        )

    def install(self) -> None:
        """Write the context and reset the per-sample gate state."""
        put("sample_id", self.sample_id)
        put("policy", self.policy)
        put("placement", self.placement)
        put("note", self.note)
        put("premise", self.premise)
        put("faults", dict(self.faults))
        put("response_override", self.response_override)
        put("fault_fired", False)
        put("faults_fired", 0)
        put("adaptive_notes", [])
        put("approvals", [])
        put("grants", {})
