import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for n in ('orderID', 'OrderID', 'orderid', 'productTemplateId', 'product_template_id', 'siteId', 'siteID'):
    hits = [t for t in rows if n in t]
    print('== %-20s %d' % (n, len(hits)))
    for h in hits[:3]: print('    ', h[:100])
