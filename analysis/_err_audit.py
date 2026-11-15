import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ErrorCatalog.cs', encoding='utf-8').read()
entries = re.findall(r'new\("([^"]+)",\s*"([^"]+)",\s*\n?\s*"([^"]+)",\s*\n?\s*"((?:[^"\\]|\\.)*)"\)', src)
print('replica ErrorCatalog entries:', len(entries))
for e in entries[:5]:
    print('   %-22s [%s] %s' % (e[0], e[1], e[2]))

# image: error-shaped strings
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
err = [t for t in rows if re.match(r'^(A|An|Could not|Failed|Unable|Invalid|The |This |Your |No |Cannot)', t) and 15 < len(t) < 200]
print()
print('image error-shaped strings:', len(err))
titles = {e[2] for e in entries}
hit = [t for t in err if any(t == x or x in t or t in x for x in titles)]
print('replica titles found in the image:', len(hit))
print()
for t in err[:10]:
    print('   -', t[:110])
