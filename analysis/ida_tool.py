"""Call an arbitrary IDA plugin tool with JSON args, so the specialised ones are reachable. (R691)

`analysis/ida.py` dispatches a fixed set of subcommands; the plugin exposes 60+ tools, several of which are built for
exactly the case this round hit (an address with no direct xref). This driver takes a tool name and a JSON argument
object so those are usable without editing the client.
"""

import json
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import ida  # noqa: E402


def main(argv):
    if len(argv) < 1:
        print("usage: python analysis/ida_tool.py <tool> [json-args]")
        return 2
    tool = argv[0]
    args = json.loads(argv[1]) if len(argv) > 1 else {}
    ida.initialize()
    res = ida.call(tool, args, timeout=900)
    print(json.dumps(res, ensure_ascii=False, indent=2)[:12000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
