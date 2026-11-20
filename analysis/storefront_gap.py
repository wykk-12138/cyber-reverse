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
    """Bare origins that sit in a dense run of other bare origins.

    A bare origin anywhere in the string database is not evidence of a store: an error message quoting
    `https://www.footlocker.ph/...` produces one too. The storefront table is recognisable by its shape -- an
    alphabetised run of bare origins packed close together -- so each hit is kept only when at least three
    others sit within 0x800 bytes of it. That is a structural filter rather than a hostname one, and it is
    the difference between "the image mentions this host" and "the image lists this store".
    """
    hits = []
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        if '\t' not in line:
            continue
        addr, text = line.split('\t', 1)
        match = BARE_ORIGIN.match(text.strip())
        if not match:
            continue
        try:
            hits.append((int(addr, 16), match.group(1).lower()))
        except ValueError:
            continue

    hits.sort()
    addresses = [a for a, _ in hits]
    kept = set()
    import bisect
    for index, (addr, host) in enumerate(hits):
        lo = bisect.bisect_left(addresses, addr - 0x800)
        hi = bisect.bisect_right(addresses, addr + 0x800)
        if hi - lo >= 4:                      # itself plus three neighbours
            kept.add(host)
    print('bare origins seen: %d   inside a dense run: %d' % (len(hits), len(kept)))
    return kept


# Second-level labels that a registrable domain includes: `401games.ca` is two labels, `argos.co.uk` three.
SECOND_LEVEL = {
    'co.uk', 'com.au', 'com.br', 'com.cn', 'com.hk', 'com.mx', 'com.my', 'com.pl', 'com.sg', 'com.tr',
    'com.tw', 'co.jp', 'co.kr', 'co.nz', 'co.za', 'co.in', 'co.il', 'co.id', 'co.th', 'ne.jp', 'or.jp',
    'com.ar', 'com.co', 'com.pe', 'com.ph', 'com.vn', 'com.ua', 'com.ru', 'net.au', 'org.uk', 'ac.uk',
    'gov.uk', 'org.au', 'net.br', 'gov.br', 'com.es', 'com.it', 'com.de', 'com.fr', 'co.ae', 'com.qa',
}


def registrable(host):
    """The registrable domain: last two labels, or three when the last two are a known second-level."""
    parts = host.lower().split('.')
    if len(parts) >= 3 and '.'.join(parts[-2:]) in SECOND_LEVEL:
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:])


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
    print('image bare origins: %d   replica domain literals: %d' % (len(origins), len(replica)))

    known = {registrable(d) for d in replica}
    print('replica registrable domains: %d' % len(known))

    def covered(host):
        root = registrable(host)
        return root in known or host in known

    missing = sorted(h for h in origins
                     if not covered(h) and not any(word in h for word in INFRA))
    roots = sorted({registrable(h) for h in missing})
    print('bare origins with no catalogue module: %d' % len(missing))
    print('of those, distinct registrable domains: %d' % len(roots))

    if '--roots' in argv:
        for root in roots[:limit]:
            print('  %s' % root)
        if len(roots) > limit:
            print('  ... %d more' % (len(roots) - limit))
        return 0

    if '--write-doc' in argv:
        doc = 'docs/STOREFRONT_SURFACE.md'
        rows = [
            '# 镜像的店铺面 vs 复刻件（由 `python analysis/storefront_gap.py --write-doc` 生成）',
            '',
            '> **这张表说的是"未列名"，不是"未处理"**：复刻件的 `ShopifyFlow` 是通用 flow，',
            '> 任何 Shopify 店都能跑。没有目录条目只说明**没有这家店的专用条目**。',
            '',
            '| 项 | 值 |',
            '|---|---|',
            '| 镜像里的裸源站（`https://host` / `https://www.host`，密集成串者） | %d |' % len(origins),
            '| 复刻件源码里形如域名的字面量 | %d |' % len(replica),
            '| 其中可归并到注册域 | %d |' % len(known),
            '| 无对应条目的主机 | %d |' % len(missing),
            '| 无对应条目的**注册域** | **%d** |' % len(roots),
            '',
            '## 方法上的两个筛子',
            '',
            '- **只收裸源站**（不带路径的 `https://host`）——报错信息里引用过的 URL 由此被挡掉。',
            '- **只收密集成串者**（±0x800 字节内有 ≥3 个同类）——镜像的店铺表是字典序大表，',
            '  孤立的裸源站多半出现在别的语境里。',
            '- 基础设施词表（支付 / CDN / 分析 / 证书）在脚本里显式列出，可被反驳。',
            '',
            '## 未列名的注册域（前 %d 个，按字典序）' % min(len(roots), 200),
            '',
            '| 注册域 |',
            '|---|',
        ]
        for root in roots[:200]:
            rows.append('| `%s` |' % root)
        if len(roots) > 200:
            rows.append('')
            rows.append('> 其余 %d 个：`python analysis/storefront_gap.py --roots --limit %d`。' % (
                len(roots) - 200, len(roots)))
        rows.append('')
        io.open(doc, 'w', encoding='utf-8', newline='').write('\n'.join(rows))
        print('wrote %s' % doc)

    for host in missing[:limit]:
        print('  %s' % host)
    if len(missing) > limit:
        print('  ... %d more' % (len(missing) - limit))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
