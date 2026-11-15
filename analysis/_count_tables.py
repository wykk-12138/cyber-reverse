import io, re, os
# count the tables' entries from source, so the record has the real number
total = 0
detail = []
for dp, _d, fns in os.walk(r'D:\projects\cyber-reverse\replica\src'):
    for fn in fns:
        if not fn.endswith('.cs'):
            continue
        t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>\(StringComparer\.Ordinal\)\s*\{(.*?)\n    \};', t, re.S):
            n = len(re.findall(r'^\s*\["', m.group(1), re.M))
            total += n
            detail.append((fn, n))
print('tables:', len(detail), '| total strings:', total)
for fn, n in detail: print('   %-26s %d' % (fn, n))
