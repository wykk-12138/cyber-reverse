import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ErrorCatalog.cs', encoding='utf-8').read()
entries = re.findall(r'new Entry\("([^"]+)",\s*"([^"]+)",\s*"([^"]*)"', src)
print('replica ErrorCatalog entries:', len(entries))
tags = {}
for _id, tag, title in entries:
    tags[tag] = tags.get(tag, 0) + 1
print('by tag:', tags)

lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
pool = set(rows)
# how many replica titles exist verbatim in the image, and how many detail sentences
hit_title = [t for _i, _g, t in entries if t in pool]
print('titles found verbatim in image:', len(hit_title), '/', len(entries))
missing = [t for _i, _g, t in entries if t not in pool]
for t in missing[:8]:
    print('   not in pool:', t)
# and: image strings that look like a bracketed catalog title but are not in the replica
bracketed = sorted({t for t in rows if re.match(r'^\[(General|Shopify|Footsites|Supreme|Nike|Yeezy)\]\s', t)})
print()
print('bracketed titles in image:', len(bracketed))
ours = {t for _i, _g, t in entries}
for t in bracketed:
    if t not in ours:
        print('   image has, replica lacks:', t)
