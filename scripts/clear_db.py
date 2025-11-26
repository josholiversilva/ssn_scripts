#!/usr/bin/env python3
"""Clear SQLite database files in a project.

Usage examples:
  # Dry-run: list matches but don't delete
  python scripts\clear_db.py --dry-run

  # Backup and delete all found .db files (non-recursive excludes .venv and .git)
  python scripts\clear_db.py --backup --yes

  # Provide a custom glob pattern
  python scripts\clear_db.py --pattern "**/instance/*.db"

This script is safe by default (dry-run) and will prompt before deleting unless --yes is passed.
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
from datetime import datetime
from pathlib import Path
import sys


EXCLUDE_DIRS = {".venv", ".git", "node_modules"}


def find_db_files(root: Path, pattern: str = "**/*.db") -> list[Path]:
    # Use rglob for recursive search; then filter by excluding common directories
    results: list[Path] = []
    for p in root.rglob(pattern.replace("**/", "")):
        # rglob with pattern like '*.db' will already walk directories, so check pattern
        if p.is_file():
            # skip if any excluded dir is in the path parts
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            results.append(p)
    # also try glob with pattern if user provided explicit subpath like 'instance/*.db'
    # For user's convenience, allow path-like patterns too.
    if any(ch in pattern for ch in ("/", "\\")):
        for p in root.glob(pattern):
            if p.is_file() and not any(part in EXCLUDE_DIRS for part in p.parts):
                if p not in results:
                    results.append(p)
    return sorted(set(results))


def backup_file(path: Path, backup_dir: Path | None = None) -> Path:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        dest = backup_dir / f"{path.name}.{ts}.bak"
    else:
        dest = path.with_name(f"{path.name}.{ts}.bak")
    shutil.copy2(path, dest)
    return dest


def remove_files(files: list[Path], backup: bool = False, backup_dir: Path | None = None) -> None:
    for f in files:
        try:
            if backup:
                b = backup_file(f, backup_dir)
                print(f"Backed up {f} -> {b}")
            f.unlink()
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find and delete .db files in a project (safe by default).")
    p.add_argument("--dry-run", action="store_true", help="Don't delete; only list matched files.")
    p.add_argument("--backup", action="store_true", help="Create backups before deleting")
    p.add_argument("--backup-dir", type=str, default=None, help="Directory to place backups (relative to cwd)")
    p.add_argument("--pattern", type=str, default="**/*.db", help="Glob pattern to search for (default: **/*.db)")
    p.add_argument("--yes", action="store_true", help="Don't prompt; proceed to delete")
    p.add_argument("--root", type=str, default=".", help="Root directory to search (default: project root)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    pattern = args.pattern
    print(f"Searching in: {root}")
    print(f"Pattern: {pattern}")
    files = find_db_files(root, pattern=pattern)
    if not files:
        print("No .db files found.")
        return 0
    print("Found the following database files:")
    for f in files:
        print("  -", f)

    if args.dry_run:
        print("Dry-run mode; no files will be deleted.")
        return 0

    if not args.yes:
        ok = input("Delete these files? [y/N]: ").strip().lower()
        if ok not in ("y", "yes"):
            print("Aborted by user.")
            return 0

    backup_dir = Path(args.backup_dir).resolve() if args.backup_dir else None
    if args.backup and backup_dir is None:
        # default backup dir is ./db_backups
        backup_dir = root / "db_backups"

    remove_files(files, backup=args.backup, backup_dir=backup_dir)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
