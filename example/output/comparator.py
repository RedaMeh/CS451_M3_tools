#!/usr/bin/env python3
"""
Compare lattice-agreement output files for comparability.

Given:
  x = number of processes (files 1.output .. x.output)
  y = number of lines per file to compare (typically #decisions)

For every pair (i, j), i != j, and for every line k in [1..y]:
  S_i(k) ⊆ S_j(k)  OR  S_j(k) ⊆ S_i(k)

This matches the "chain / comparability" requirement: all decided sets on the same
line index must be comparable.

Usage:
  python compare_outputs.py x y [--dir PATH] [--allow-empty] [--trim]

Notes:
- Each line is a set of space-separated integers, e.g. "12 13 2 9"
- Empty line is treated as empty set only if --allow-empty is set.
- By default, if a file has < y lines, that's an error.
"""

import argparse
from pathlib import Path
import sys


def parse_line_to_set(line: str, allow_empty: bool) -> set[int]:
    line = line.strip()
    if not line:
        if allow_empty:
            return set()
        raise ValueError("empty line encountered (use --allow-empty to allow)")
    parts = line.split()
    try:
        return {int(p) for p in parts}
    except ValueError as e:
        raise ValueError(f"non-integer token in line: {line!r}") from e


def read_sets(filepath: Path, y: int, allow_empty: bool, trim: bool) -> list[set[int]]:
    if not filepath.exists():
        raise FileNotFoundError(f"missing file: {filepath}")

    lines = filepath.read_text(encoding="utf-8", errors="strict").splitlines()

    if trim:
        # drop trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()

    if len(lines) < y:
        raise ValueError(f"{filepath.name} has {len(lines)} lines, expected at least {y}")

    sets = []
    for idx in range(y):
        sets.append(parse_line_to_set(lines[idx], allow_empty))
    return sets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("x", type=int, help="number of processes (expects files 1.output..x.output)")
    ap.add_argument("y", type=int, help="number of lines per file to compare")
    ap.add_argument("--dir", type=str, default=".", help="directory containing output files")
    ap.add_argument("--allow-empty", action="store_true", help="treat empty lines as empty sets")
    ap.add_argument("--trim", action="store_true", help="ignore trailing empty lines at end of files")
    args = ap.parse_args()

    x, y = args.x, args.y
    if x <= 0 or y <= 0:
        print("x and y must be positive integers.", file=sys.stderr)
        return 2

    out_dir = Path(args.dir)
    if not out_dir.is_dir():
        print(f"--dir is not a directory: {out_dir}", file=sys.stderr)
        return 2

    # Load all outputs
    decided: dict[int, list[set[int]]] = {}
    try:
        for i in range(1, x + 1):
            fp = out_dir / f"{i}.output"
            decided[i] = read_sets(fp, y, args.allow_empty, args.trim)
    except Exception as e:
        print(f"ERROR reading outputs: {e}", file=sys.stderr)
        return 1

    violations = []

    # Check comparability per line index across all pairs
    for k in range(y):
        for i in range(1, x + 1):
            Si = decided[i][k]
            for j in range(i + 1, x + 1):
                Sj = decided[j][k]
                if not (Si.issubset(Sj) or Sj.issubset(Si)):
                    violations.append((k + 1, i, j, Si, Sj))

    if not violations:
        print(f"OK: All {x} files are comparable on each of the first {y} lines.")
        return 0

    print(f"FAIL: Found {len(violations)} comparability violation(s).")
    # Print up to first 20 violations to avoid huge output
    for idx, (line_no, i, j, Si, Sj) in enumerate(violations[:20], start=1):
        print(f"\nViolation {idx}: line {line_no} -> {i}.output vs {j}.output are incomparable")
        print(f"  {i}.output[{line_no}] = {sorted(Si)}")
        print(f"  {j}.output[{line_no}] = {sorted(Sj)}")
        # Show quick set differences
        print(f"  {i} \\ {j} = {sorted(Si - Sj)}")
        print(f"  {j} \\ {i} = {sorted(Sj - Si)}")

    if len(violations) > 20:
        print(f"\n...and {len(violations) - 20} more.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
