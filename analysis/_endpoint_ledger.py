import io, re, glob
def api_like(p):
    low = p.lower()
    if any(low.endswith(x) for x in ('.png','.jpg','.jpeg','.gif','.svg','.ico','.css','.js','.json','.woff','.woff2','.ttf')):
        return False
    if low.startswith('/assets/') or low.startswith('/.well-known/'):
        return False
    segs = [s for s in p.split('/') if s]
    if not segs: return False
    if any(len(s) > 12 and re.match(r'^[A-Za-z0-9_\-]+$', s) and not s.islower() for s in segs):
        return False
    return True

src_paths = {}
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'"((?:/[A-Za-z0-9_\-.{}$*]+){2,})"', t):
        p = m.group(1)
        if api_like(p): src_paths.setdefault(p, set()).add(f.split('replica\\')[-1])

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
pool = set(rows)

verbatim, composed, none = [], [], []
for p, files in src_paths.items():
    if p in pool:
        verbatim.append(p); continue
    segs = [s for s in p.split('/') if s]
    tail2 = '/' + '/'.join(segs[-2:]) if len(segs) >= 2 else None
    tail1 = '/' + segs[-1] if segs else None
    if (tail2 and any(x.endswith(tail2) or tail2 in x for x in rows)) or (tail1 and tail1 in pool):
        composed.append(p)
    else:
        none.append((p, sorted(files)))

print('replica API paths: %d' % len(src_paths))
print('  verbatim in image : %d' % len(verbatim))
print('  composed of parts : %d' % len(composed))
print('  NO evidence       : %d' % len(none))
print()
for p, files in none[:20]:
    print('   %-42s %s' % (p, files[0]))
