import io, re, glob
# replica: GraphQL-ish operation names used as strings
ops = {}
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'"(query|mutation)\s+(\w+)|operationName["\s:]+"(\w+)"|"(\w+(?:GraphQL|Graphql|Query|Mutation))"', t):
        name = m.group(2) or m.group(3) or m.group(4)
        if name: ops.setdefault(name, set()).add(f.split('replica\\')[-1].replace('\\','/'))
print('replica graphql-ish names:', len(ops))

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (pat.match(l) for l in lines) if m}
hit = [n for n in ops if n in pool]
miss = sorted(n for n in ops if n not in pool)
print('in pool: %d   not in pool: %d' % (len(hit), len(miss)))
for n in miss[:20]:
    print('   %-34s %s' % (n, sorted(ops[n])[0]))
