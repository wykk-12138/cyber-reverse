"""Probe the replica IDA instance (port 13338) for analysis readiness. (R694)

`analysis/ida.py` hardcodes 13337 (the original). This talks to an arbitrary port so the replica instance can be
checked -- which matters because the plugin answered on 13338 only about a minute after the PDB was loaded, and a
55 MB NativeAOT cannot be fully analysed in a minute. A count taken before `auto_analysis_ready` is a partial
measurement, not a result.
"""

import json
import sys
import urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13338
URL = "http://127.0.0.1:%d/mcp" % PORT
_id = [0]


def rpc(method, params=None, timeout=180):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "probe", "version": "1"}})
    res = rpc("tools/call", {"name": "server_health", "arguments": {}})
    print(json.dumps(res, ensure_ascii=False, indent=2)[:1500])


if __name__ == "__main__":
    main()
