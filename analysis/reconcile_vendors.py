"""Reconcile the anti-bot vendor list: what the replica knows, what the image names. (R807)

Criterion (f) asks for the original's store and risk-vendor lists taken from the binary, checked item by item against
Registry.cs and the flow sources. This does the risk half: read the replica's declared vendor set, then probe the
image for those names and for a wider set of vendors the replica does not declare.
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
IDA = os.path.join(ROOT, "analysis", "ida.py")


def find_vendors_in_replica():
    names = set()
    for base, _d, files in os.walk(os.path.join(ROOT, "replica", "src")):
        if os.sep + "obj" in base or os.sep + "bin" in base:
            continue
        for f in files:
            if not f.endswith(".cs"):
                continue
            t = io.open(os.path.join(base, f), encoding="utf-8", errors="replace").read()
            m = re.search(r"AntiBotVendors[^{]*\{(.*?)\}", t, re.S)
            if not m:
                continue
            for lit in re.findall(r'"([^"]+)"', m.group(1)):
                names.add(lit)
    return sorted(names)


def probe(pattern):
    out = subprocess.run([sys.executable, IDA, "str", pattern], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return 0
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return 0
    return len(d.get("matches", []))


declared = find_vendors_in_replica()
print("  replica AntiBotVendors: %d" % len(declared))
for d in declared:
    print("    " + d)

print()
CANDIDATES = [
    "kasada", "cloudflare", "datadome", "perimeterx", "px-captcha", "queue-it", "queueit",
    "akamai", "incapsula", "imperva", "shape", "distil", "reblaze", "radware", "aws-waf",
    "funcaptcha", "arkose", "hcaptcha", "recaptcha", "turnstile", "datadog", "forter",
    "signifyd", "riskified", "adyen", "stripe", "braintree", "cybersource", "sift",
]
print("  candidate vendors against the image:")
missing_from_replica = []
for c in CANDIDATES:
    n = probe(c)
    inrep = any(c.lower() in d.lower() for d in declared)
    flag = ""
    if n > 0 and not inrep:
        flag = "   <-- in image, not declared"
        missing_from_replica.append((c, n))
    print("    %-16s image=%-4d replica=%-5s%s" % (c, n, "yes" if inrep else "no", flag))

print()
print("  in the image but not declared: %d" % len(missing_from_replica))
for c, n in missing_from_replica:
    print("    %-16s %d" % (c, n))
