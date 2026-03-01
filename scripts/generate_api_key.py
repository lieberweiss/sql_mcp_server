#!/usr/bin/env python3
from __future__ import annotations

import argparse
import secrets
import string
import sys
from pathlib import Path

ALL_SCOPES = {"r", "w", "a", "d"}
DEFAULT_TOKENS = Path(__file__).resolve().parents[1] / "tokens.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate MCP API key entries (username:token:scopes)"
    )
    parser.add_argument("username", help="Logical username (e.g. agent name)")
    parser.add_argument(
        "--scopes",
        default="rw",
        help="Scopes to grant (subset of rwad). Default: %(default)s",
    )
    parser.add_argument(
        "--token",
        help="Optional token to use. When omitted a random token is generated.",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Token length (ignored when --token is provided). Default: %(default)s",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TOKENS,
        help=f"Tokens file path (default: {DEFAULT_TOKENS})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print entry instead of writing to the tokens file",
    )
    return parser.parse_args()


def generate_token(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def append_entry(path: Path, entry: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry + "\n")


def main() -> None:
    args = parse_args()
    scopes = {c.lower() for c in args.scopes if c.strip()}
    unknown = scopes - ALL_SCOPES
    if unknown:
        sys.exit(f"Unsupported scope(s): {''.join(sorted(unknown))}. Allowed: rwad")

    token = args.token or generate_token(args.length)
    entry = f"{args.username}:{token}:{''.join(sorted(scopes))}"
    if args.stdout:
        print(entry)
    else:
        append_entry(args.file, entry)
        print(f"Entry appended to {args.file}")


if __name__ == "__main__":
    main()
