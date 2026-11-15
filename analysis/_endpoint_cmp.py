import io, re, glob, os
# every path-like literal in the replica's source
paths_src = set()
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'"((?:/[A-Za-z0-9_\-.{}$*]+){2,})"', t):
        paths_src.add(m.group(1))
print('distinct path literals in the replica:', len(paths_src))

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
paths_pool = {t for t in rows if re.match(r'^(?:/[A-Za-z0-9_\-.{}$*]+){2,}$', t)}
print('distinct path literals in the image  :', len(paths_pool))

common = paths_src & paths_pool
print('both        :', len(common))
print('replica only:', len(paths_src - paths_pool))
print('image only  :', len(paths_pool - paths_src))
print()
print('image only (前 20):')
for p in sorted(paths_pool - paths_src)[:20]: print('   ', p)
