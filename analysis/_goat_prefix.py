import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
checks = {
 '/web-api/v1/buys': ['web-api/v1/buys', 'web-api'],
 '/web-api/v1/countries': ['web-api/v1/countries'],
 '/web-api/v1/product_variants/buy_bar_data': ['buy_bar_data', 'product_variants'],
}
for want, needles in checks.items():
    print('== 期望有效路径', want)
    for n in needles:
        hits = [r for r in rows if n in r][:3]
        print('   %-34s %d 处' % (n, len([r for r in rows if n in r])))
        for h in hits: print('        ', h[:95])
