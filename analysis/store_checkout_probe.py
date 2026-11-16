"""Which of the eleven unfinished modules have evidenced checkout endpoints? (R767)

R766 closed scheels by pointing two new steps at endpoints that were already declared and never called. Before doing
that again, this asks the same question for the rest: does the image name a checkout surface per store?

A store with `checkout`, `payment`, `shipping`, `cart`-style actions in its own host strings is a candidate for the
same treatment. A store whose only strings are a product/drops/raffle surface is a shape mismatch, and the seven-step
yardstick is the wrong question for it -- the distinction R765 flagged for goat and R766 confirmed.

**Why not an existing tool** (AGENTS.md §1.2): this is `search_strings` per domain, eight times. The plugin does the
search; what is added is the grouping into checkout-shaped versus other, and the per-store verdict.
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

STORES = [
    ("bstn", ["bstn.com"]),
    ("casio", ["casio.com"]),
    ("fanatics", ["fanatics.com", "lids.com"]),
    ("hbx", ["hbx.com"]),
    ("hypecommerce", ["hypecommerce"]),
    ("offspring", ["offspring.co.uk", "offspring.com"]),
    ("warhammer", ["warhammer.com"]),
    ("yeezysupply", ["yeezysupply.com"]),
]

# Words that make a store's surface a checkout rather than a raffle or a feed.
CHECKOUT = re.compile(r"(checkout|payment|shipping|delivery|cart|order|basket|billing)", re.I)
# Words that make it something else on purpose.
OTHER = re.compile(r"(drop|raffle|enter|feed|release|lottery|waiting|queue)", re.I)


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def strings_for(domain):
    d = call("str", re.escape(domain))
    return [m for m in (d or {}).get("matches", []) if domain in m.get("string", "")]


def main():
    rows = []
    for name, domains in STORES:
        hits = []
        for dom in domains:
            hits.extend(strings_for(dom))
        # dedupe by address and keep the URL-ish ones
        seen, keep = set(), []
        for m in hits:
            if m["addr"] in seen:
                continue
            seen.add(m["addr"])
            s = m["string"]
            if "://" in s or s.startswith("/"):
                keep.append(s)
        co = sorted({s for s in keep if CHECKOUT.search(s)})
        ot = sorted({s for s in keep if OTHER.search(s)})
        verdict = "CHECKOUT" if co and len(co) >= len(ot) else ("OTHER-SHAPE" if ot else "NO-URLS")
        rows.append((name, len(keep), len(co), len(ot), verdict, co[:6], ot[:3]))

    print("  %-13s %-8s %-9s %-7s %s" % ("store", "urls", "checkout", "other", "verdict"))
    print("  " + "-" * 96)
    for name, total, nc, no, verdict, co, ot in rows:
        print("  %-13s %-8d %-9d %-7d %s" % (name, total, nc, no, verdict))

    print()
    for name, total, nc, no, verdict, co, ot in rows:
        if verdict == "CHECKOUT":
            print("  %s -- checkout-shaped endpoints:" % name)
            for s in co:
                print("      %s" % s[:104])
        elif ot:
            print("  %s -- other shape:" % name)
            for s in ot:
                print("      %s" % s[:104])
    return 0


if __name__ == "__main__":
    sys.exit(main())
