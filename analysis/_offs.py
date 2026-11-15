import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
for n in (159052, 159053):
    m = re.match(r'^\s*(0x[0-9a-f]+)', src[n-1])
    print(n, m.group(1))
