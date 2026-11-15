"""Dump a run of .NET UTF-16 string literals from the binary.

Round 50: reading bytes around `checkoutCardsinkCallerIdentificationSignature` showed the
neighbourhood is an alphabetically-ordered pool of camelCase JSON keys:

    checkoutAgreements
    checkoutAsGuest
    checkoutAttemptId
    checkoutCardsinkCallerIdentificationSignature
    checkoutConfig

If they are ordered, a whole payload's field names can be recovered by walking the range instead
of guessing each one. This decodes a window and prints every literal-length-prefixed string in it.

Usage:
    python dump_strings.py <start_hex> <size> [filter-substring]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ida_mcp


def fetch(addr: int, size: int) -> bytes:
    body, _ = ida_mcp.post({
        "jsonrpc": "2.0", "id": "7", "method": "tools/call",
        "params": {"name": "get_bytes",
                   "arguments": {"regions": [{"addr": hex(addr), "size": size}]}},
    }, ida_mcp.handshake())
    out = ida_mcp.parse_result(body)
    if not isinstance(out, list) or not out:
        return b""
    data = out[0].get("data", "")
    return bytes(int(b, 16) for b in data.split())


def literals(blob: bytes):
    """Yield (offset, text) for each .NET length-prefixed UTF-16 literal in the blob."""
    i = 0
    n = len(blob)
    while i + 8 <= n:
        # .NET string literal: int32 length at i, then length UTF-16 code units at i+4
        length = int.from_bytes(blob[i:i + 4], "little")
        if 1 <= length <= 300 and i + 4 + length * 2 <= n:
            raw = blob[i + 4:i + 4 + length * 2]
            try:
                text = raw.decode("utf-16-le")
            except UnicodeDecodeError:
                i += 1
                continue
            if text and all(32 <= ord(ch) < 0x3000 for ch in text):
                yield i, text
                i += 4 + length * 2
                # literals are 8-byte aligned; skip padding
                while i + 8 <= n and blob[i:i + 8] == b"\x00" * 8:
                    i += 8
                continue
        i += 1


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    start = int(sys.argv[1], 16)
    size = int(sys.argv[2], 0)
    needle = sys.argv[3] if len(sys.argv) > 3 else None

    blob = fetch(start, size)
    print(f"read {len(blob)} bytes at {hex(start)}", file=sys.stderr)

    out = []
    for off, text in literals(blob):
        if needle and needle.lower() not in text.lower():
            continue
        out.append((start + off, text))

    print(f"{len(out)} literal(s)\n")
    for ea, text in out:
        print(f"  {ea:#x}  {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
