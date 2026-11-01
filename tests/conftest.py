"""Shared fixtures: an in-process stand-in for the Docker sandbox.

The fake dispatches the harness's fixed argv against a local SQLite file per
sample, so the approver, tools, scorer and oracle run exactly as they do in the
container, minus Docker. These tests are not isolation evidence.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "tool_effect_bench"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


registry = load_module("teb_registry", PACKAGE / "sandbox" / "registry.py")
CASES: list[dict[str, Any]] = json.loads(
    (PACKAGE / "fixtures" / "cases.json").read_text(encoding="utf-8")
)


def ok(stdout: str) -> SimpleNamespace:
    return SimpleNamespace(success=True, stdout=stdout, stderr="", returncode=0)


def failed(message: str) -> SimpleNamespace:
    return SimpleNamespace(success=False, stdout="", stderr=message, returncode=2)


class FakeSandbox:
    """Run the fixed registry commands against local files, one DB per sample."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.commands: list[list[str]] = []

    def database(self, sample_id: str) -> Path:
        return self.root / sample_id / "registry.sqlite3"

    async def exec(self, cmd: list[str], **kwargs: Any) -> SimpleNamespace:
        from tool_effect_bench import context
        from tool_effect_bench.solvers import PROBE_KEYS

        self.commands.append(list(cmd))
        sample_id = str(context.get("sample_id"))
        db = self.database(sample_id)
        try:
            if cmd[:2] == ["python", "/opt/registry.py"]:
                args = cmd[2:]
                if len(args) == 2 and args[0] == "init":
                    db.parent.mkdir(parents=True, exist_ok=True)
                    registry.initialize(db, args[1])
                    out: dict[str, Any] = {"initialized": True}
                elif len(args) == 2 and args[0] == "inspect_artifact":
                    out = registry.inspect_artifact(db, args[1])
                elif len(args) == 5 and args[0] == "mutate":
                    out = registry.mutate(db, *args[1:])
                elif args == ["probe"]:
                    out = dict.fromkeys(PROBE_KEYS, True)
                else:
                    raise ValueError("unsupported fixed command")
                return ok(json.dumps(out, sort_keys=True))
            evidence = db.parent / "evidence.sqlite3"
            if cmd == ["python", "/opt/snapshot.py"]:
                if evidence.exists():
                    raise FileExistsError("evidence already exported")
                with (
                    sqlite3.connect(f"{db.as_uri()}?mode=ro", uri=True) as reader,
                    sqlite3.connect(evidence) as writer,
                ):
                    reader.backup(writer)
                return ok("")
            if cmd == ["base64", "/state/evidence.sqlite3"]:
                return ok(base64.b64encode(evidence.read_bytes()).decode())
            if cmd == ["sha256sum", "/state/evidence.sqlite3"]:
                digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
                return ok(f"{digest}  /state/evidence.sqlite3")
            raise ValueError("unsupported command")
        except (
            ValueError,
            RuntimeError,
            sqlite3.Error,
            FileExistsError,
            FileNotFoundError,
        ) as error:
            return failed(str(error))


@pytest.fixture
def fake_sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FakeSandbox:
    from tool_effect_bench import scorer, solvers, tools

    sandbox = FakeSandbox(tmp_path / "sandboxes")
    for module in (scorer, solvers, tools):
        monkeypatch.setattr(module, "sandbox", lambda: sandbox)
    return sandbox
