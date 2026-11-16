"""Poll a late-binding IDA instance until its plugin reports ready. (R707)

**Why this exists** (project convention §1.2): `analysis/wait_ready.py` polls `server_health`, but it treats a refused
connection as fatal, so it exits immediately when the plug-in has not bound its port yet. That is exactly the state the
replica instance is in while auto-analysis runs -- IDA binds the port near the end, so "connection refused" is the normal
intermediate answer, not an error.

It also prints the process CPU delta each round, because wall-clock and working-set both lie about progress: R694 was
diagnosed by CPU delta standing still while a modal dialog waited, and the same signal is what distinguishes "thinking"
from "stuck" here.

Usage: python analysis/poll_ready.py <port> <timeout_sec> [pid]
"""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ID = [0]


def rpc(url, method, params=None, timeout=20):
    ID[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": ID[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def cpu_seconds(pid):
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Id %d -ErrorAction SilentlyContinue).CPU" % pid],
            capture_output=True, text=True, timeout=25).stdout.strip()
        return float(out) if out else None
    except (ValueError, subprocess.SubprocessError):
        return None


def main(argv):
    port = int(argv[0]) if argv else 13338
    timeout = int(argv[1]) if len(argv) > 1 else 900
    pid = int(argv[2]) if len(argv) > 2 else None
    url = "http://127.0.0.1:%d/mcp" % port

    deadline = time.time() + timeout
    last_cpu = None
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        cpu = cpu_seconds(pid) if pid else None
        delta = "" if (cpu is None or last_cpu is None) else " (cpu +%.1fs)" % (cpu - last_cpu)
        last_cpu = cpu if cpu is not None else last_cpu

        try:
            rpc(url, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                    "clientInfo": {"name": "poll-ready", "version": "1"}})
            res = rpc(url, "tools/call", {"name": "server_health", "arguments": {}}, timeout=60)
            health = json.loads(res["result"]["content"][0]["text"])
            ready = health.get("auto_analysis_ready")
            print("[%3d] port %d up: ready=%r idb=%s%s"
                  % (attempt, port, ready, health.get("idb_path"), delta), flush=True)
            if ready is True:
                print("READY", json.dumps(health), flush=True)
                return 0
        except (urllib.error.URLError, ConnectionError, socket.error, TimeoutError):
            print("[%3d] port %d not listening yet%s" % (attempt, port, delta), flush=True)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            print("[%3d] port %d answered but not with health: %s%s" % (attempt, port, exc, delta), flush=True)

        time.sleep(10)

    print("TIMEOUT after %ds" % timeout, flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
