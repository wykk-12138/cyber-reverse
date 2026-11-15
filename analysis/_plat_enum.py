import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
# 1) every string that looks like an enum member of an input/quantity family
fam = re.compile(r'^(Input[A-Z]\w*|Quantity\w*|MultiCart\w*|AutoQuantity\w*)$')
hits = [(a, t) for a, t in rows if fam.match(t.strip())]
print('enum-ish names:', len(hits))
for a, t in hits[:24]:
    print('  ', a, t[:60])
print()
# 2) locale-ish platform keys
loc = [(a, t) for a, t in rows if re.search(r'Platform\.|Stores?\.[A-Z]', t) and len(t) < 80]
print('platform-ish keys:', len(loc))
for a, t in loc[:16]:
    print('  ', a, t[:70])
