import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
def around(needle, before=2, after=2, limit=3):
    print('==', needle)
    n = 0
    for i, (a, t) in enumerate(rows):
        if needle in t:
            for j in range(max(0, i - before), min(len(rows), i + after + 1)):
                mark = '>>' if j == i else '  '
                print(' ', mark, rows[j][0], rows[j][1][:120])
            print('  ---')
            n += 1
            if n >= limit: break
around('AddToCartPreload', 2, 2, 2)
around('CompletePayPalGuestPayment', 1, 1, 2)
