import io
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
for n in range(159600, 159700):
    t = src[n-1][12:]
    if t.strip():
        print(f'{n:7d} ind={len(t)-len(t.lstrip()):2d} {t[:145]}')
