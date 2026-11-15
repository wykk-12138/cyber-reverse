import io, re, glob
def api_like(p):
    low = p.lower()
    if any(low.endswith(x) for x in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js', '.json', '.woff', '.woff2', '.ttf')):
        return False
    if low.startswith('/assets/') or low.startswith('/.well-known/'):
        return False
    segs = [s for s in p.split('/') if s]
    if not segs: return False
    # drop segments that look like random tokens
    if any(len(s) > 12 and re.match(r'^[A-Za-z0-9_\-]+$', s) and not s.islower() for s in segs):
        return False
    return True

paths_src = set()
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'"((?:/[A-Za-z0-9_\-.{}$*]+){2,})"', t):
        if api_like(m.group(1)): paths_src.add(m.group(1))

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
paths_pool = {t for t in rows if re.match(r'^(?:/[A-Za-z0-9_\-.{}$*]+){2,}$', t) and api_like(t)}

print('API-like paths — replica: %d   image: %d   both: %d' % (len(paths_src), len(paths_pool), len(paths_src & paths_pool)))
print()
print('=== 复刻件有、镜像没有（可能是自造 —— 需要复核）: %d' % len(paths_src - paths_pool))
for p in sorted(paths_src - paths_pool)[:24]: print('   ', p)
