"""Write every source file into report/appendix_code.md (guideline: "print your code and include it
in the appendix"). Owner: Member 1. Implemented.

    python -m lrrep.report.code_appendix

Convert to PDF with any Markdown tool (e.g. `pandoc report/appendix_code.md -o appendix_code.pdf`),
or paste into the report document.
"""
from __future__ import annotations

from pathlib import Path

from lrrep.config import REPO_ROOT

INCLUDE = ["config.yaml", "src/lrrep/**/*.py"]
SKIP_NAMES = {"__init__.py"}


def build(out: Path | None = None) -> Path:
    out = out or REPO_ROOT / "report" / "appendix_code.md"
    files: list[Path] = []
    for pattern in INCLUDE:
        files += sorted(p for p in REPO_ROOT.glob(pattern) if p.name not in SKIP_NAMES)
    parts = ["# Appendix: Code\n",
             "All results are produced by `python -m lrrep.pipeline --all` from this code.\n"]
    for p in files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        lang = "yaml" if p.suffix == ".yaml" else "python"
        parts.append(f"\n## `{rel}`\n\n```{lang}\n{p.read_text().rstrip()}\n```\n")
    out.write_text("\n".join(parts))
    return out


def run(fake: bool = False) -> None:
    print(f"wrote {build()}")


if __name__ == "__main__":
    run()
