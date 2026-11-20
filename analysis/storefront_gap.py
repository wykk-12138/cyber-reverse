"""Which storefront domains the image knows and the replica has no module for.

WHY THIS EXISTS: two whole stores turned up by accident (Saucony in R1308, AO in R1313) and both were found
by reading a neighbourhood rather than by asking the question directly. The image keeps its storefronts in an
alphabetised table of bare-origin URLs -- `https://www.saucony.com`, `https://ao.com` and their neighbours --
so the question can be asked directly.

The FIRST version of this script answered 1557 uncovered hosts in 1355 domains, which is nonsense and was
nonsense for two reasons worth keeping:
  - it took every https host in the string database, so CA-OCSP URLs, error-message hosts and analytics all
    counted as shops;
  - it read the replica's domains with its own regex and found 50 of them, while the catalogue has 67 modules
    -- so most of the "gap" was the replica side of the subtraction being wrong, exactly the shape of the
    mistakes this project has recorded about scanners that assume a form.

So: the image side is restricted to bare origins (the storefront table's shape), and the replica side comes
from `tools/store_catalog.py`, the tool that already parses the catalogue correctly, instead of a second
opinion that disagrees with it.

Usage: python analysis/storefront_gap.py [--limit N]
"""
import io
import re
import subprocess
import sys

DUMP = 'analysis/ida_strings.txt'

# A bare origin: scheme, host, optional trailing slash, nothing else. That is the storefront table's shape.
BARE_ORIGIN = re.compile(r'^https?://(?:www\.)?([A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z]{2,})/?$')

# Infrastructure that appears as a bare origin but is not a shop. Listed so a reader can disagree.
INFRA = (
    'google', 'gstatic', 'googleapis', 'recaptcha', 'hcaptcha', 'cloudflare', 'akamai', 'jsdelivr',
    'cloudfront', 'fastly', 'newrelic', 'nr-data', 'sentry', 'datadome', 'perimeterx', 'kasada',
    'queue-it', 'adyen', 'stripe', 'paypal', 'cybersource', 'square', 'braintree', 'klarna', 'shopify',
    'myshopify', 'demobaza', 'amazonaws', 'azure', 'microsoft', 'aka.ms', 'w3.org', 'schema.org',
    'github', 'npmjs', 'nuget', 'facebook', 'twitter', 'youtube', 'instagram', 'tiktok', 'linkedin',
    'gpayments', 'komoju', 'degica', 'touchtechpayments', 'omise', 'midtrans', 'paynamics', 'sibs',
    'commercehub', 'mollie', 'worldpay', 'cardinalcommerce', 'airwallex', '2c2p', '2captcha',
)


def image_origins():
    origins = set()
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        if '\t' not in line:
            continue
        _, text = line.split('\t', 1)
        match = BARE_ORIGIN.match(text.strip())
        if match:
            origins.add(match.group(1).lower())
    return origins


def replica_domains():
    """Every domain-shaped string literal anywhere in replica/src.

    Three earlier versions under-counted, each for the same reason -- assuming a form:
      - scanning only Modules/ found 50, because most flows live in Flows/;
      - parsing the catalogue tool's table found 36, because the column is truncated;
      - scanning `Domains => new[] {...}` found 77, because the registry also writes domains inline:
        `new FlowStoreModule(new ShopifyFlow("100thieves", "100 Thieves", new[] { "100thieves.com" }))`.
    So the surface is taken whole: any quoted string that looks like a domain, anywhere under src. Over-
    including is the safe direction for a gap question -- it can hide a store, not invent one.
    """
    import os
    shaped = re.compile(r'"([a-z0-9][a-z0-9.\-]*\.[a-z]{2,})"', re.I)
    domains = set()
    for root, dirs, files in os.walk('replica/src'):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if not name.endswith('.cs'):
                continue
            text = io.open(os.path.join(root, name), encoding='utf-8', errors='replace').read()
            for match in shaped.finditer(text):
                domains.add(match.group(1).lower())
    return domains


def main(argv):
    limit = 80
    if '--limit' in argv:
        limit = int(argv[argv.index('--limit') + 1])

    origins = image_origins()
    replica = replica_domains()
    print('image bare origins: %d   catalogue domains parsed: %d' % (len(origins), len(replica)))

    def covered(host):
        return any(host == d or host.endswith('.' + d) or d.endswith('.' + host) for d in replica)

    missing = sorted(h for h in origins
                     if not covered(h) and not any(word in h for word in INFRA))
    print('bare origins with no catalogue module: %d' % len(missing))
    for host in missing[:limit]:
        print('  %s' % host)
    if len(missing) > limit:
        print('  ... %d more' % (len(missing) - limit))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
