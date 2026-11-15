import io, re, glob
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
hits = sorted({r for r in rows if r.startswith('PublishTemplate.')})
print('PublishTemplate.* keys:', len(hits))
for h in hits: print('   ', h)
print()
print('复刻件里有没有 PublishTemplate:')
found = False
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    if 'PublishTemplate' in t:
        print('   ', f.replace('D:\\projects\\cyber-reverse\\replica\\',''))
        found = True
print('   (none)' if not found else '')
