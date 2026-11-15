import io, re, json
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
d_state = re.compile(r'<(\w+)>d__(\d+)')

loose = []
for a, t in rows:
    ds = d_state.findall(t)
    if len(ds) >= 2:
        loose.append((a, [[int(o), n] for n, o in ds]))

print('rows with >=2 d__ (lambda NOT required):', len(loose))
print('steps in those rows:', sum(len(s) for _, s in loose))

jl = [(a, s) for a, s in loose if any(n == 'GetProductHtml' for _, n in s)]
print()
print('rows containing GetProductHtml:', len(jl))
for a, s in jl:
    print(' ', a, '->', ', '.join('%d:%s' % (o, n) for o, n in s))
