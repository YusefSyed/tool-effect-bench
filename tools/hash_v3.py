"""Print the freeze hashes of the v0.3 suite (paper/V03-PROTOCOL.md).

Samples are hashed the way the v0.2 suite was: JSON with sorted keys, a newline,
then the system prompt. One hash per prompt arm.

Usage: uv run python tools/hash_v3.py [dump-path]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tool_effect_bench.dataset import PROMPTS
from tool_effect_bench.dataset_v3 import build_v3_samples


def main() -> None:
    for prompt, (system, _) in PROMPTS.items():
        samples = build_v3_samples(prompt=prompt)
        blob = (
            json.dumps([s.model_dump(mode="json") for s in samples], sort_keys=True)
            + "\n"
            + system
        )
        print(prompt, len(samples), hashlib.sha256(blob.encode()).hexdigest())
        if len(sys.argv) > 1:
            Path(f"{sys.argv[1]}.{prompt}").write_text(blob, encoding="utf-8")


if __name__ == "__main__":
    main()
