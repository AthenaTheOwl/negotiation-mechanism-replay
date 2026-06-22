from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF_RE = re.compile(r"R-NMR-\d{3}")
DEF_RE = re.compile(r"^##\s+(R-NMR-\d{3})\b", re.MULTILINE)
SCAN_ROOTS = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "docs", ROOT / "specs"]


def iter_markdown() -> list[Path]:
    paths: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            paths.append(root)
        elif root.exists():
            paths.extend(sorted(root.rglob("*.md")))
    return paths


def main() -> int:
    definitions: set[str] = set()
    references: dict[str, list[Path]] = {}

    for path in iter_markdown():
        text = path.read_text(encoding="utf-8", errors="replace")
        definitions.update(DEF_RE.findall(text))
        for ref in REF_RE.findall(text):
            references.setdefault(ref, []).append(path)

    missing = sorted(ref for ref in references if ref not in definitions)
    if missing:
        for ref in missing:
            locations = ", ".join(str(path.relative_to(ROOT)) for path in references[ref])
            print(f"missing definition: {ref} referenced by {locations}", file=sys.stderr)
        return 1

    print(f"ok: {len(definitions)} requirement definitions, {len(references)} referenced ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
