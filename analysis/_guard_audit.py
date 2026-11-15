import io, re, glob
susp = []
for f in glob.glob(r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    if 'File.ReadAllText' not in t: continue
    for m in re.finditer(r'Assert\.(Contains|DoesNotContain)\(', t):
        # find the statement text
        start = m.start()
        stmt = t[start:start+240].split(';')[0]
        if 'File.ReadAllText' in stmt or re.search(r'\b(text|source|script|guide|doc)\b', stmt):
            susp.append((f.split('\\')[-1], stmt.replace('\n', ' ')[:110]))
seen = set(); out = []
for f, s in susp:
    k = (f, s[:60])
    if k in seen: continue
    seen.add(k); out.append((f, s))
print('file-level Contains assertions:', len(out))
for f, s in out[:16]: print('  %-34s %s' % (f, s))
