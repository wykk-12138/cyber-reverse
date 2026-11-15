import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]

print('=== johnlewis 附近：找 b__21_ / b__22_ 的归属 ===')
for a, t in rows:
    if re.search(r'b__(21|22)_\d', t):
        print('  0x%08x  %s' % (a, t[:150]))

print()
print('=== nike：四个缺口名的 d__ 形态 ===')
for name in ('StartEcomSession', 'Authorize', 'GetAccessToken', 'FindVariant'):
    hits = [(a, t) for a, t in rows if name in t]
    print('--', name, len(hits))
    for a, t in hits[:3]:
        print('   0x%08x  %s' % (a, t[:120]))
