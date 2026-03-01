#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_TOKENS = Path(__file__).resolve().parents[1] / "tokens.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove an MCP API key by username")
    parser.add_argument("username", help="Username to remove")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TOKENS,
        help=f"Tokens file path (default: {DEFAULT_TOKENS})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.file.exists():
        sys.exit(f"Tokens file {args.file} does not exist")

    lines = args.file.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"{args.username}:")]

    if len(kept) == len(lines):
        sys.exit(f"No entry found for username {args.username}")

    args.file.write_text("\n".join(filter(None, kept)) + ("\n" if kept else ""), encoding="utf-8")
    print(f"Removed entries for {args.username} from {args.file}")


if __name__ == "__main__":
    main()
