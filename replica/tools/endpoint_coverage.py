r"""Endpoint coverage, measured once with one extraction.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):

The same question was measured five times between R892 and R900 and got five answers, because each round wrote a
fresh throwaway script with a different assumption baked in:

    R892   family scan anchored at /x/vN/        -> "40 families absent", then 32 after a storage-form fix
    R894   family-level presence                 -> 17 / 45
    R895   path level, tail matching allowed     -> 55 / 171
    R900   full-path scan, verbatim only         -> 49 / 154, and 27 paths shown to have been truncated

Two of those rounds documented their own figure as "the accurate one". The differences were never about the target;
they were about the scan. A number that changes because the script changed is not a measurement.

So there is one extraction, here, and one matching rule, here. Anything that wants a coverage figure runs this.

THE EXTRACTION, and what it assumes:

    A path is a literal beginning with a slash, containing at least one more segment, and containing a /segment/vN/
    family somewhere. It is captured from its first character, so a prefix in front of the family survives. R892's
    pattern started at the family and therefore dropped prefixes; R900 showed that affected twenty-seven paths.

    An optional host is captured from //host in the same literal. Host and path in one literal is co-occurrence,
    which is evidence of ownership. Host absent means ownership is unknown at path level and the row says so.

THE MATCHING, and why it is verbatim only:

    A path counts as covered when the exact string appears as a string literal in the replica's source. Nothing
    looser. R895 also accepted a path's tail after its family segment, which is how a Base-plus-tail constant is
    stored -- but that rule also matches a tail under a different base, and it was one of the reasons R895's figure
    is not comparable with R900's. Storage variants are handled by listing them, not by widening the test.

    A path the replica holds under a different form therefore counts as missing here. That is deliberate: this tool
    measures "does the replica string together this exact path", and a caller who wants storage-aware matching has to
    say so and cite it.

Reproduce:

    cd D:\projects\cyber-reverse
    python analysis\ida.py py "exec(open(r'D:/projects/cyber-reverse/analysis/coverage_extract.py', encoding='utf-8').read(), {})"
    cd replica && python tools\endpoint_coverage.py

World split:

    Hosts are classified store or vendor from an explicit list below, because the two answer different questions.
    R896 measured the mixed figure at 32.2 percent and showed it was the average of 38.7 and 0.0; averaging a
    denominator over unlike things produced a number that was neither.

Output is stable and line-oriented so a metrics runner can read one key per line.
"""

import io
import json
import os
import sys

ROOT = r"D:\projects\cyber-reverse"
EXTRACT = os.path.join(ROOT, "analysis", ".coverage-paths.txt")
REPLICA_SRC = os.path.join(ROOT, "replica", "src")

# A vendor is a payment processor, a protection service or another third party whose endpoints a store calls but
# does not own. Every other host is a store. The list is explicit so a host cannot drift between buckets unnoticed.
VENDOR = {
    "challenges.cloudflare.com",
    "flex.cybersource.com",
    "www.paypal.com",
    "app.midtrans.com",
    "checkoutshopper-live.adyen.com",
    "api.braintreegateway.com",
    "api.sibspayments.com",
    "www.vivapayments.com",
    "payments.bigcommerce.com",
    "webservices.global-e.com",
    "static-forms.klaviyo.com",
    "pbiouukmdvahsphokqle.supabase.co",
    "inbox-api.aycd.io",
    "api.vipps.no",
    "www.ibm.com",
    "api.tobe-official.jp",
    "authenticate.riotgames.com",
    "degica.as1.gpayments.net",
    "ecommerce-gateway.mollie.com",
    "forms.shopifyapps.com",
    "api.upsellit.com",
    "www.target.com",
    "bolt.eu",
}


def load():
    if not os.path.exists(EXTRACT):
        sys.exit("run the extraction first: see this file's docstring")

    raw = io.open(EXTRACT, encoding="utf-8", errors="replace").read()
    i = raw.find("{")
    if i < 0:
        sys.exit("extraction output is not JSON; re-run analysis/coverage_extract.py")
    d, _ = json.JSONDecoder().raw_decode(raw[i:])
    res = (d.get("result") or "") + (d.get("stdout") or "")

    rows = []
    for line in res.splitlines():
        if not line.startswith("F\t"):
            continue
        _, host, path = line.split("\t")
        # a URL matched from its two slashes captures the host as the first segment; drop it so the path is the path
        seg = path.split("/")
        if host != "-" and len(seg) > 1 and seg[1] == host:
            path = "/" + "/".join(seg[2:])
        rows.append((host, path))
    return rows


def replica_text():
    parts = []
    for dp, _dirs, fs in os.walk(REPLICA_SRC):
        if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
            continue
        for fn in fs:
            if fn.endswith(".cs"):
                try:
                    parts.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
                except OSError:
                    pass
    return "\n".join(parts)


def main():
    rows = load()
    text = replica_text()

    buckets = {
        "store": {"total": 0, "have": 0},
        "vendor": {"total": 0, "have": 0},
        "hostless": {"total": 0, "have": 0},
    }

    missing = []
    for host, path in rows:
        if host == "-":
            key = "hostless"
        elif host in VENDOR:
            key = "vendor"
        else:
            key = "store"
        buckets[key]["total"] += 1
        if ('"' + path + '"') in text:
            buckets[key]["have"] += 1
        else:
            missing.append((key, host, path))

    print("coverage: paths recovered %d" % len(rows))
    for key in ("store", "vendor", "hostless"):
        b = buckets[key]
        pct = (100.0 * b["have"] / b["total"]) if b["total"] else 0.0
        print("coverage: %s paths %d" % (key, b["total"]))
        print("coverage: %s covered %d" % (key, b["have"]))
        print("coverage: %s percent %.1f" % (key, pct))

    print("coverage: missing %d" % len(missing))
    if "-v" in sys.argv:
        for key, host, path in missing:
            print("  %-8s %-34s %s" % (key, host[:34], path))


if __name__ == "__main__":
    main()
