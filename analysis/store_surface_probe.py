"""Does the original carry a checkout surface for these three stores? (R769)

R765 read the coverage matrix and called eleven modules unfinished because SubmitShippingAsync and
SubmitPaymentAsync were absent. R766 and R767 closed two by pointing them at endpoints the image already named.
R768 found the third case is different: offspring's surface is a Poq platform host, so its API family is wrong rather
than its steps.

So before touching fanatics, warhammer or yeezysupply, the question is whether the image carries a checkout surface for
them at all. If it does not, then 71% is the yardstick being applied to the wrong object, and the honest record is
"the original has no per-store checkout here" rather than "we have not built it yet".

The form question matters (AGENTS.md 2.7). A checkout can appear as:

  * a path under the store's own host          hbx.com/checkout/pay
  * a third-party platform host with a client  platform.poq.io/clients/offspring/checkout/start
  * an action on an API hub                    apihub.scheels.com/frontastic/action/cart/checkout
  * a GraphQL mutation, which is not a URL     api.prod.warhammer.com/graphql

So this dumps every string that mentions the store, not just URL-shaped ones, and reports which of the four forms the
evidence supports.

**Why not an existing tool** (AGENTS.md §1.2): `search_strings` per name. What is added is the form taxonomy above and
the refusal to call "no URL path" the same thing as "no checkout".
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

STORES = [
    ("fanatics", ["fanatics"]),
    ("warhammer", ["warhammer", "games-workshop"]),
    ("yeezysupply", ["yeezysupply"]),
]

CHECKOUT = re.compile(r"(checkout|payment|shipping|delivery|billing|order|cart|basket|purchase|pay\b)", re.I)
GRAPHQL = re.compile(r"(graphql|/gql|query\s|mutation)", re.I)
PLATFORM = re.compile(r"(poq|frontastic|salesforce|commercetools|bigcommerce|shopify|magento|hybris|centra|"
                      r"shopware|vtex|sap|soldsie|queue-it|kasada|datadome)", re.I)


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def main():
    for name, tokens in STORES:
        seen, strings = set(), []
        for tok in tokens:
            d = call("str", re.escape(tok))
            for m in (d or {}).get("matches", []):
                if m["addr"] in seen:
                    continue
                seen.add(m["addr"])
                s = m["string"]
                if tok.lower() in s.lower():
                    strings.append(s)

        urls = sorted({s for s in strings if "http://" in s or "https://" in s})
        co = sorted({s for s in strings if CHECKOUT.search(s)})
        gq = sorted({s for s in strings if GRAPHQL.search(s)})
        pl = sorted({s for s in strings if PLATFORM.search(s)})

        print("  === %s ===" % name)
        print("    strings=%d  urls=%d  checkout=%d  graphql=%d  platform=%d"
              % (len(strings), len(urls), len(co), len(gq), len(pl)))
        for label, group in (("url", urls), ("checkout", co), ("graphql", gq), ("platform", pl)):
            for s in group[:6]:
                print("      [%s] %s" % (label, s[:92].replace("\n", " ")))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
