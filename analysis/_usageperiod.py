import io
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    public TimeSpans? UsageExpiry { get; set; }'''
add1 = '''    /// <summary>
    /// How long a usage period lasts, beside <see cref="UsageExpiry"/> (bound and persisted as <c>usagePeriod</c>).
    /// </summary>
    /// <remarks>
    /// R389: a real 5.18.32 backup writes both <c>usagePeriod</c> and <c>usageExpiry</c> on every task group
    /// (<c>Backups/Backup 14 Nov 08h01m.cyb</c>), while this model only had the expiry. The two are separate fields in the
    /// image, so they are separate here.
    /// </remarks>
    public TimeSpans? UsagePeriod { get; set; }

''' + anchor1
assert anchor1 in t1 and 'public TimeSpans? UsagePeriod' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor1, add1, 1))
print('TaskGroup.UsagePeriod added')

p2 = None
import os
for dp, _d, fns in os.walk(r"D:\projects\cyber-reverse\replica\src"):
    for fn in fns:
        if fn.endswith('.cs'):
            t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
            if 'class ProxyGroup' in t:
                p2 = os.path.join(dp, fn); break
    if p2: break
print('ProxyGroup file:', p2)
t2 = io.open(p2, encoding='utf-8').read()
import re
m = re.search(r'class ProxyGroup\b', t2)
i = t2.index('{', m.end()); depth = 0
for j in range(i, len(t2)):
    if t2[j] == '{': depth += 1
    elif t2[j] == '}':
        depth -= 1
        if depth == 0:
            body = t2[i:j]; break
print('has UsageExpiry:', 'UsageExpiry' in body, '| has UsagePeriod:', 'UsagePeriod' in body)
