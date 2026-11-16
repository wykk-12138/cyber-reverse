"""Work out what AntiBotVendors actually is, before treating it as the vendor inventory. (R807)

Nine entries, all Datadome or Forter specifics. The image names eighteen other vendors. Before writing "eighteen
missing", find where the vendors that ARE handled live -- the flows demonstrably deal with Akamai on fanatics and AWS
WAF on Warhammer without appearing in that list, so the list is something narrower.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica\src"


def where(needle):
    hits = []
    for base, _d, files in os.walk(ROOT):
        if os.sep + "obj" in base or os.sep + "bin" in base:
            continue
        for f in files:
            if not f.endswith(".cs"):
                continue
            p = os.path.join(base, f)
            t = io.open(p, encoding="utf-8", errors="replace").read()
            for i, line in enumerate(t.splitlines(), 1):
                if needle in line:
                    hits.append((os.path.relpath(p, ROOT), i, line.strip()))
    return hits


print("  --- AntiBotVendors declaration and uses ---")
for path, i, line in where("AntiBotVendors"):
    print("    %-46s %4d  %s" % (path, i, line[:88]))

print()
print("  --- where the vendors that ARE handled appear ---")
for v in ("Akamai", "kasada", "Kasada", "QueueIt", "queue-it", "PerimeterX",
          "PerimeterX", "shape", "Turnstile", "hcaptcha"):
    hits = where(v)
    if hits:
        print("    %-14s %d hit(s)" % (v, len(hits)))
        for path, i, line in hits[:4]:
            print("        %-40s %4d  %s" % (path, i, line[:66]))
