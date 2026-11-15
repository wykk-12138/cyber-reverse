import io
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
for n in list(range(158575, 158606)) + [158616, 158617, 158618]:
    t = src[n-1][12:]
    print(f'{n:7d} ind={len(t)-len(t.lstrip()):2d} {t[:110]}')
