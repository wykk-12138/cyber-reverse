"""For each module with no pool hit, try the other forms the image might use. (R813)

Section 2.7: ask how many forms a thing can take before concluding it is absent. The first pass searched the module id
and its vanity domain. A Shopify store can appear as <slug>.myshopify.com, as the bare slug, or as a path fragment, so
those forms are tried before any of the eight is called unsupported.
"""

import io

ROOT = r"D:\projects\cyber-reverse"
POOL = ROOT + r"\analysis\pe_strings.txt"

SUSPECTS = {
    "bodega": ["bodega"],
    "bstn": ["bstn"],
    "nike-gs": ["nike-gs", "nikegs", "kids.nike"],
    "offthehook": ["offthehook", "off-the-hook", "oth"],
    "saintalfred": ["saintalfred", "saint-alfred"],
    "shophmvs": ["shophmvs", "hmvs"],
    "trophyroom": ["trophyroom", "trophy-room", "trophy"],
    "voo": ["vooberlin", "voo"],
}

pool = io.open(POOL, encoding="utf-8", errors="replace").read()
low = pool.lower()

print("  per suspect, every form tried:")
for mid, forms in SUSPECTS.items():
    print("    %s" % mid)
    any_hit = False
    for f in forms:
        for suffix in ("", ".myshopify.com", "myshopify", ".com", "-", "_"):
            needle = (f + suffix).lower()
            n = low.count(needle)
            if n:
                any_hit = True
                print("        %-28s %d" % (needle, n))
    if not any_hit:
        print("        (no form matched)")

print()
print("  myshopify hosts in the pool, as a cross-check:")
import re
hosts = sorted(set(re.findall(r"([a-z0-9][a-z0-9\-]{1,40})\.myshopify\.com", low)))
print("    %d distinct myshopify slugs" % len(hosts))
print("    " + ", ".join(hosts[:40]))
