"""Wait for an IDA instance's auto-analysis to finish, judged by the readiness flag. (R694, documented R696)

Port-open is the wrong signal: the plugin answers as soon as it is loaded, while analysis is still running. This polls
`server_health.auto_analysis_ready` and exits 0 only when it flips to true.

**This replaces two earlier criteria, and the reason matters:**

  * R433 used "the window title no longer says Loading" plus "two consecutive samples agree". The second half does not
    work: the intermediate state is *stable*. R433's wrong/right ratio was 136,798/187,328 = 0.730; R694's was
    136,989/187,732 = 0.730, 260 rounds later. Two samples in that window can agree and both be wrong.
  * R613 already polled `auto_analysis_ready`, so the good criterion existed before this file did -- it just lived in a
    report instead of in the code that takes the measurement. Keeping it here is the point.

Operational steps: `docs/IDA_STARTUP_CHECKLIST.md` ("端口开 ≠ 分析完"). Original record: `docs/PARITY_PRODUCT.md` §8.

Usage: python analysis/wait_ready.py [port] [timeout_sec]
"""

import json
import sys
import time
import urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13338
TIMEOUT = int(sys.argv[2]) if len(sys.argv) > 2 else 1800
URL = "http://127.0.0.1:%d/mcp" % PORT
_id = [0]


def rpc(method, params=None, timeout=60):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def health():
    res = rpc("tools/call", {"name": "server_health", "arguments": {}})
    text = res["result"]["content"][0]["text"]
    return json.loads(text)


def main():
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "waiter", "version": "1"}})
    started = time.time()
    last = None
    while time.time() - started < TIMEOUT:
        try:
            h = health()
        except Exception as exc:
            print("  poll failed: %s" % exc)
            time.sleep(20)
            continue
        key = (h.get("auto_analysis_ready"), h.get("strings_cache_size"))
        if key != last:
            print("  t+%3ds  auto_analysis_ready=%s  strings=%s"
                  % (int(time.time() - started), h.get("auto_analysis_ready"), h.get("strings_cache_size")))
            last = key
        if h.get("auto_analysis_ready"):
            print("READY after %d s" % int(time.time() - started))
            return 0
        time.sleep(20)
    print("TIMEOUT after %d s" % TIMEOUT)
    return 1


if __name__ == "__main__":
    sys.exit(main())
