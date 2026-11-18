"""R1143: re-probe the scheme-bearing literals without their scheme.

The first pass compared each literal exactly as written in the source, so `https://api.paypal.com/v2/
checkout/orders` was tested only with its scheme. The image may well carry `api.paypal.com/v2/...`
without one, and calling that "invented" would be an accusation built on the shape of my own probe.
This re-tests every scheme-bearing candidate in both the absent and the errored columns.
"""
import json
import re
import subprocess

PY = r"python"
IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

verdict = json.loads(open(r"D:\projects\cyber-reverse\analysis\.flow_url_verdict.json",
                          encoding="utf-8").read())
lits = [r["literal"] for r in verdict["confirmed_absent"]] + \
       [r["literal"] for r in verdict["search_errored"]]
schemed = [l for l in lits if l.startswith("http")]


def probe(pattern):
    p = subprocess.run([PY, IDA, "str", re.escape(pattern), "--limit", "3"],
                       capture_output=True, text=True, timeout=300)
    out = p.stdout
    try:
        i = out.find("{")
        d = json.JSONDecoder().raw_decode(out[i:])[0]
        return d.get("n", 0)
    except Exception:
        return -1


print("scheme-bearing candidates:", len(schemed))
results = {}
for lit in schemed:
    bare = lit.split("://", 1)[1]
    n_bare = probe(bare)
    # also try the host alone: the machine may store scheme-less host + path separately
    host = bare.split("/", 1)[0]
    n_host = probe(host)
    results[lit] = {"bare": n_bare, "host": n_host}
    print("   bare=%-3s host=%-3s  %s" % (n_bare, n_host, lit[:70]))

open(r"D:\projects\cyber-reverse\analysis\.flow_url_scheme.json", "w", encoding="utf-8").write(
    json.dumps(results, indent=2))
