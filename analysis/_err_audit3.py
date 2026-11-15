import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ErrorCatalog.cs', encoding='utf-8').read()
# titles with escaped quotes preserved
blocks = re.findall(r'new Entry\("([^"]+)",\s*"([^"]+)",\s*"((?:[^"\\]|\\.)*)"', src)
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (pat.match(l) for l in lines) if m}

def unescape(s):
    return s.replace('\\"', '"').replace('\\\\', '\\')

ok = bad = 0
for _id, _tag, raw in blocks:
    t = unescape(raw)
    if t in pool: ok += 1
    else:
        bad += 1
        print('title not in pool:', t)
print('titles verbatim: %d / %d' % (ok, len(blocks)))

# details: collect the string(s) after the title line
detail_ok = 0
for m in re.finditer(r'new Entry\("[^"]+",\s*"[^"]+",\s*"(?:[^"\\]|\\.)*",\s*\n?\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*\n?\s*)+)', src):
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
    text = unescape(''.join(parts))
    if text in pool: detail_ok += 1
    else: print('   detail not verbatim:', text[:90])
print('details verbatim: %d / %d' % (detail_ok, len(blocks)))
