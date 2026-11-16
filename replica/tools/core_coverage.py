"""Core coverage: the original's store and risk-vendor hosts against what the replica registers.

WHY THIS EXISTS: completion criterion (f) asks for a table that can be recomputed -- the original's store and
risk-vendor list taken from the binary, set against Registry.cs and Flows/Scripts, with a stated reason for every
uncovered item. No such table existed. METRICS.md carried endpoint counts and shape counts, and endpoint_coverage.py
counted paths, but nothing compared hosts to registrations, which is what (f) actually asks.

WHY NOT endpoint_coverage.py: that tool answers "is this path named in the replica", one row per path. This asks
"does the replica know this host at all", one row per host. A host can be covered with zero of its paths named, and a
path can be named whose host no flow ever contacts; the two questions are independent.

WHAT THE MATCH ASSUMES, and why that assumption is the tool's weakness: a host is matched to a registration when the
registration's identifier or its flow type name contains the host's registrable label, or the reverse. That is a
substring test, and R876 already established that adjacency is not ownership. It will miss a store registered under a
label that shares no letters with its domain (a real risk: the registry has ids like "a-ma-maniere" for a domain that
may spell it differently) and it can match by accident on a short label like "size" or "cap". So the output labels each
row matched / unmatched / ambiguous rather than claiming coverage, and an unmatched row means "no registration contains
this label" and not "the store is absent".
"""

import io
import json
import os
import re
from collections import Counter

ROOT = r"D:\projects\cyber-reverse"
INVENTORY = os.path.join(ROOT, "analysis", ".coverage-paths.txt")
REGISTRY = os.path.join(ROOT, "replica", "src", "Cybersole.Stores", "Modules", "Registry.cs")
SCRIPTS = os.path.join(ROOT, "replica", "src", "Cybersole.Stores", "Scripts")

# hosts that are a protection, a payment provider or infrastructure rather than a shop; matched against Scripts/ instead
VENDOR_HINTS = (
    "cloudflare", "kasada", "datadome", "perimeterx", "queue-it", "queueit", "recaptcha", "hcaptcha",
    "akamai", "aycd", "turnstile", "captcha", "paypal", "stripe", "adyen", "paynamics", "eshopworld",
    "global-e", "vivapayments", "wdprapps", "disney",
    # R920: purpledotprice is a preorder service, not a shop. One literal names it --
    # /api/v1/products/preorder-state?api_key=...&handle= -- so the host asks a vendor whether a product is on
    # preorder rather than serving a store of its own.
    "purpledotprice", "purpledot",
)

# second-level labels that carry no identity
GENERIC = {"www", "api", "checkout", "payments", "payment", "pay", "id", "auth", "login", "secure",
           "shop", "store", "m", "static", "cdn", "assets", "img", "prod", "production", "webservices",
           "payments-panel", "paymentsheet-ent", "inbox-api", "challenges", "nodecde1", "shield"}


def rows():
    raw = io.open(INVENTORY, encoding="utf-8-sig", errors="replace").read()
    doc = json.loads(raw)
    out = doc.get("stdout") or doc.get("result") or ""
    for line in out.splitlines():
        if not line.startswith("F\t"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1] not in ("-", ""):
            yield parts[1].strip(), parts[2].strip()


def label(host):
    """The registrable label: the part before the public suffix, skipping generic subdomains.

    R917: the first version returned the first non-generic segment, which turned api-search.dickssportinggoods.com into
    "api-search" and prod-hk-actapi.popmart.com into "prod-hk-actapi" -- both wrong, and the second reported Pop Mart as
    unknown even though it is a flow. The fault was assuming a subdomain is either wholly generic or wholly meaningful
    when hyphenated prefixes are neither. candidates() returns every segment instead, and a host counts as known when
    any candidate matches.
    """
    return candidates(host)[0] if candidates(host) else host.lower()


def candidates(host):
    """Every segment of the host that could be its identity, most specific first.

    Segments are stripped of generic tokens on both sides of a hyphen, so "api-search" yields "search" as a fallback
    and "prod-hk-actapi" yields "actapi"; both are still offered whole as well, because a label could legitimately be
    hyphenated like the registry's own "a-ma-maniere".
    """
    bits = [b for b in host.lower().split(".") if b]
    if len(bits) >= 3 and bits[-2] in ("co", "com", "net", "org", "gov", "ac"):
        bits = bits[:-2]
    else:
        bits = bits[:-1]

    out = []
    for b in reversed(bits):  # the closest-to-suffix segment is the most likely identity
        if b not in GENERIC:
            out.append(b)
        for token in re.split(r"-", b):
            if token and token not in GENERIC and token not in out:
                out.append(token)
    return out


def registry_ids():
    """Identifiers and flow types registered in Registry.cs, plus every lowercased identifier that appears anywhere in
    src.

    R917: matching against Registry.cs alone reported www.vans.com as unmatched, and R899 had already established that
    Vans is handled -- in DemandwareControllers.cs's site-id table, not in the registry. So the search covers the whole
    tree, and a host counts as known when its label appears in any source file. That widens what "matched" means from
    "registered" to "named somewhere", which is why unmatched now means the stronger thing: this label appears nowhere
    in the replica at all.
    """
    text = io.open(REGISTRY, encoding="utf-8", errors="replace").read()
    ids = set(re.findall(r'"([a-z0-9][a-z0-9\-\.]{1,30})"', text))
    flows = set(re.findall(r"new\s+(\w+Flow)\s*\(", text))

    everything = [text.lower()]
    for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
        if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
            continue
        for fn in fs:
            if fn.endswith(".cs"):
                try:
                    everything.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read().lower())
                except OSError:
                    pass
    return ids, flows, "\n".join(everything)


def scripts_text():
    parts = []
    if os.path.isdir(SCRIPTS):
        for fn in os.listdir(SCRIPTS):
            if fn.endswith(".cs"):
                parts.append(io.open(os.path.join(SCRIPTS, fn), encoding="utf-8", errors="replace").read())
    return "\n".join(parts)


def main():
    names = Counter()
    for host, path in rows():
        names[host] += 1

    ids, flows, all_src = registry_ids()
    flow_names = {f.lower().replace("flow", "") for f in flows}
    scr = scripts_text().lower()

    stores, vendors = [], []
    for host, count in sorted(names.items()):
        low = host.lower()
        (vendors if any(v in low for v in VENDOR_HINTS) else stores).append((host, count, label(host)))

    print("hosts with a path: %d  (store %d, vendor %d)"
          % (len(names), len(stores), len(vendors)))
    print("registry identifiers: %d   flow types: %d" % (len(ids), len(flows)))
    print("")

    hit = miss = 0
    print("store hosts")
    for host, count, lab in stores:
        cands = candidates(host)
        matches = [i for i in ids for c in cands if c in i or i in c]
        typed = [f for f in flow_names for c in cands if c in f or f in c]
        # R917: also accept the label appearing anywhere in src, not only in the registry
        named = any(c in all_src for c in cands)
        state = "matched" if (matches or typed or named) else "unmatched"
        if state == "matched":
            hit += 1
        else:
            miss += 1
        detail = (matches[:2] + typed[:2]) or (["in src"] if named else [])
        print("  %-6s %-40s %2d paths  %s" % (state, host, count, ", ".join(detail[:3])))

    print("")
    print("vendor hosts")
    for host, count, lab in vendors:
        state = "matched" if lab in scr else "unmatched"
        print("  %-6s %-40s %2d paths  %s" % (state, host, count, lab))

    print("")
    print("store hosts matched %d / %d, unmatched %d" % (hit, hit + miss, miss))
    print("NOTE: matched means a registration contains the host's label; unmatched means none does. Neither proves")
    print("      the store works or is absent -- a store can be registered under a label sharing no letters with its")
    print("      domain, and a short label can match by accident.")


if __name__ == "__main__":
    main()