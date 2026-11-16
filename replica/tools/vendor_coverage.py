"""Which vendor hosts the image carries have any counterpart in the replica.

WHY THIS EXISTS: criterion (f) asks for the original's store and risk-vendor list against Registry.cs and Flows/Scripts.
R917 measured the store half and R918 through R920 closed it. The vendor half was never measured -- core_coverage.py
prints vendor rows but only as a by-product of the store question, and it judges them by a single substring test against
Scripts/ alone.

So this asks the vendor question properly: for each of the twelve vendor hosts, is there a file or a literal that names
the service anywhere in src, and what is it called. The answer is a table of present/absent with a file for each
present one, so criterion (f) has the second column it was missing.

The judgement is a name search, and R730 says names are not the same as reading code. It is used only to say "nothing in
the replica mentions this service", which a search can establish, and never to say "this service is handled correctly".
"""

import io
import json
import os
import re
from collections import Counter


ROOT = r"D:\projects\cyber-reverse"
INVENTORY = os.path.join(ROOT, "analysis", ".coverage-paths.txt")
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("comment_split", os.path.join(ROOT, "replica", "tools", "comment_split.py"))
comment_split = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(comment_split)

VENDOR_HINTS = (
    "cloudflare", "kasada", "datadome", "perimeterx", "queue-it", "queueit", "recaptcha", "hcaptcha",
    "akamai", "aycd", "turnstile", "captcha", "paypal", "stripe", "adyen", "paynamics", "eshopworld",
    "global-e", "vivapayments", "wdprapps", "disney", "purpledotprice", "purpledot",
)

# the service name to look for in src, per vendor host
SERVICE = {
    "challenges.cloudflare.com": ("Cloudflare", ("cloudflare",)),
    "checkoutshopper-live.adyen.com": ("Adyen", ("adyen",)),
    "inbox-api.aycd.io": ("AYCD", ("aycd", "inbox-api")),
    "payments-panel.production.eshopworld.com": ("eShopWorld", ("eshopworld",)),
    "paymentsheet-ent.wdprapps.disney.com": ("Disney", ("disney", "wdprapps")),
    "registerdisney.go.com": ("Disney", ("disney", "registerdisney")),
    "retailer-shopifypayments-api.production.eshopworld.com": ("eShopWorld", ("eshopworld", "shopifypayments")),
    "web-dsy.global-e.com": ("Global-e", ("global-e", "global_e")),
    "webservices.global-e.com": ("Global-e", ("global-e", "global_e")),
    "www.paypal.com": ("PayPal", ("paypal",)),
    "www.vivapayments.com": ("Viva", ("viva",)),
    "www.purpledotprice.com": ("PurpleDot", ("purpledot",)),
}


def rows():
    raw = io.open(INVENTORY, encoding="utf-8-sig", errors="replace").read()
    doc = json.loads(raw)
    out = doc.get("stdout") or doc.get("result") or ""
    for line in out.splitlines():
        if line.startswith("F\t"):
            parts = line.split("\t")
            if len(parts) >= 3 and parts[1] not in ("-", ""):
                yield parts[1].strip(), parts[2].strip()


def sources():
    """Every non-comment source line, keyed by file, so a hit names a file rather than a byte offset."""
    for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
        if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
            continue
        for fn in fs:
            if not fn.endswith(".cs"):
                continue
            p = os.path.join(dp, fn)
            try:
                text = io.open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            # R925: strip comments before searching. R915 fixed this in the two method-coverage tools after a doc
            # comment made SubmitWebRtc look implemented; the same fault appeared here, where a comment in VivaPayments
            # mentioning Disney made Disney's hosts look named in a file about a different vendor. A name in prose is
            # not a name in code.
            yield os.path.relpath(p, os.path.join(ROOT, "replica")), comment_split.strip_comments(text)


def main():
    hosts = Counter(h for h, _p in rows())
    vendors = {h: c for h, c in hosts.items() if any(v in h.lower() for v in VENDOR_HINTS)}

    files = list(sources())
    print("vendor hosts carrying a path: %d" % len(vendors))
    print("")
    print("%-58s %3s  %-12s %s" % ("host", "pt", "service", "named in"))
    present = absent = 0
    for host in sorted(vendors):
        service, needles = SERVICE.get(host, (host, (host.split(".")[-2],)))
        hits = [rel for rel, text in files
                if any(n in text.lower() for n in needles)]
        # the inventory file itself and the tool that reads it are not the replica implementing anything
        hits = [h for h in hits if not h.endswith("core_coverage.py")]
        state = "yes" if hits else "NO"
        if hits:
            present += 1
        else:
            absent += 1
        print("%-58s %3d  %-12s %-4s %s" % (host, vendors[host], service, state,
                                            ", ".join(sorted(set(h.split(os.sep)[-1] for h in hits))[:3]) or "-"))

    print("")
    print("vendor hosts carrying a path: %d" % len(vendors))
    print("vendors named somewhere in src: %d" % present)
    print("vendors absent from src: %d" % absent)
    print("NOTE: 'yes' means some source file contains the service's name. It does not mean the integration is complete")
    print("      or correct -- a constant naming a host and a working flow are different things.")


if __name__ == "__main__":
    main()