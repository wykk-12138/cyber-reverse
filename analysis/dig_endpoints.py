"""Harvest the original's own strings for the endpoints the replica guessed at.

IDA has the string cache built (491,542 entries) even though full auto-analysis is still running,
so `find_regex` works while `xrefs_to` returns nothing. That is enough for the question this
answers: does the replica call the same routes as the original?

Each pattern is one find_regex call. Results are written as markdown so they can be diffed against
PARITY.md rather than pasted into chat and lost.
"""
import io
import json
import os
import sys

# The bundled python311 has a `._pth` file that keeps the script directory off sys.path, so a
# plain `import ida_mcp` fails here even though the file sits next to this one. Put it back.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ida_mcp

PATTERNS = [
    ("nike-kasada", r"(kasada|kpsdk|j-1\.2|x-kpsdk)"),
    ("nike-cart", r"(nike\.com|/api/cart|/api/checkout|launch\.nike)"),
    ("bstn", r"api/beast"),
    ("shopify-cart", r"(cart/add\.js|cart\.js|checkouts/)"),
    ("hybris", r"(basket/add|minibasket|hybris)"),
    ("magento", r"(Magento|checkout/cart/add|rest/V1)"),
    ("casio", r"(casio\.com|/us_en|AEM)"),
    ("fanatics", r"(fanatics|akamai|_abck)"),
    ("scheels", r"(scheels)"),
    ("warhammer", r"(warhammer)"),
    ("queue-it", r"(queue-it|queueit)"),
    ("captcha-hosts", r"(hcaptcha\.com|recaptcha|geetest|turnstile|funcaptcha)"),
    ("vendor-hosts", r"cybersole\.io"),
]


def scan(pattern: str, limit: int = 40) -> list[dict]:
    body, _ = ida_mcp.post({
        "jsonrpc": "2.0", "id": "9", "method": "tools/call",
        "params": {"name": "find_regex", "arguments": {"pattern": pattern, "limit": limit}},
    }, ida_mcp.handshake())
    out = ida_mcp.parse_result(body)
    if isinstance(out, dict) and "matches" in out:
        return out["matches"]
    return []


def main() -> int:
    lines = ["# 原版字符串表里的端点", "",
             "来源：`Cybersole.exe.i64` 的字符串缓存（491,542 条），`find_regex` 逐 pattern 检索。",
             "IDA 的 `auto_analysis_ready` 仍是 false，所以没有 xref——**这里只有字符串，没有调用者**。",
             ""]

    for name, pattern in PATTERNS:
        hits = scan(pattern)
        lines.append(f"## {name}  `{pattern}` — {len(hits)} 条")
        lines.append("")
        if not hits:
            lines.append("（无）")
            lines.append("")
            continue
        lines.append("| 地址 | 字符串 |")
        lines.append("|---|---|")
        for h in hits:
            s = (h.get("string") or "").replace("|", "\\|")[:160]
            lines.append(f"| `{h.get('addr')}` | `{s}` |")
        lines.append("")
        print(f"{name:16} {len(hits)}", file=sys.stderr)

    io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\endpoints.md",
            "w", encoding="utf-8").write("\n".join(lines))
    print("written to analysis/endpoints.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
