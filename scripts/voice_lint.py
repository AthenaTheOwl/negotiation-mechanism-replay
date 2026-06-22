from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETING_WORDS = {
    "best-in-class",
    "cutting-edge",
    "delightful",
    "effortless",
    "game-changing",
    "innovative",
    "seamless",
    "synergy",
    "transformative",
}
ANTITHESIS_RE = re.compile(r"\bnot\s+[^.\n]{0,80}\s+but\b", re.IGNORECASE)
SCAN_DIRS = ["README.md", "STATUS.md", "docs", "examples", "negotiations", "specs/0002-design"]


def iter_text_files() -> list[Path]:
    paths: list[Path] = []
    for item in SCAN_DIRS:
        path = ROOT / item
        if path.is_file():
            paths.append(path)
        elif path.exists():
            paths.extend(sorted(path.rglob("*.md")))
    return paths


def main() -> int:
    failures: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for word in sorted(MARKETING_WORDS):
            if re.search(rf"\b{re.escape(word)}\b", lowered):
                failures.append(f"{path.relative_to(ROOT)}: marketing word: {word}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if ANTITHESIS_RE.search(line):
                failures.append(f"{path.relative_to(ROOT)}:{line_number}: antithetical reversal")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"ok: scanned {len(iter_text_files())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
