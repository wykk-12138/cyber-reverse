import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]

print('=== johnlewis 相关：<<FindProduct>g__ 与 <AddToCart>b__ 在 0x0338a655 附近 ===')
for a, t in rows:
    if 0x0338a000 <= a <= 0x0338c000 and re.search(r'<(FindProduct|AddToCart)>', t):
        print('  0x%08x  %s' % (a, t[:160]))
print()
print('=== nike 四个名 ===')
for name in ('StartEcomSession', 'Authorize', 'GetAccessToken', 'FindVariant'):
    hits = [(a, t) for a, t in rows if re.search(r'<%s>' % name, t)]
    print('-- %-18s %d 处' % (name, len(hits)))
    for a, t in hits[:2]:
        print('   0x%08x  %s' % (a, t[:130]))
