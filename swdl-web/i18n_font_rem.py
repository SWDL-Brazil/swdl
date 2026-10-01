"""Convert fixed micro font sizes (8/9/10/11px) to rem so they scale with html font-size."""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent

# floor: never smaller than ~11.5px at 17px root after conversion intent
REPLACEMENTS = {
    "text-[8px]": "text-[0.62rem]",    # ~10.5px @17 — floor for micro labels
    "text-[9px]": "text-[0.68rem]",    # ~11.6px
    "text-[10px]": "text-[0.72rem]",   # ~12.2px
    "text-[11px]": "text-[0.75rem]",   # ~12.75px
}

EXTS = {".tsx", ".ts", ".css"}
SKIP_DIRS = {"node_modules", ".next", "dist", ".git"}

changed = 0
for path in ROOT.rglob("*"):
    if path.suffix not in EXTS or not path.is_file():
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    new = text
    for old, rep in REPLACEMENTS.items():
        new = new.replace(old, rep)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        changed += 1
        print(path.relative_to(ROOT))

print(f"files changed: {changed}")
