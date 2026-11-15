import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\CandidateSteps.cs', encoding='utf-8').read()
cands = re.findall(r'new Candidate\("([^"]+)",\s*(\d+),\s*"([^"]*)"\)', src)
print('candidates:', len(cands))
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (pat.match(l) for l in lines) if m}
dnames = set(re.findall(r'<(\w+)>d__\d+', '\n'.join(pool)))
for name, ordv, coll in cands:
    where = 'd__' if name in dnames else ('plain' if name in pool else 'NOT FOUND')
    colls = [c.strip() for c in coll.split(',')]
    bad = [c for c in colls if c not in ('none', '') and c not in dnames and c not in pool]
    print('  %-30s %3s  %-9s  碰撞里找不到的: %s' % (name, ordv, where, bad or '-'))
