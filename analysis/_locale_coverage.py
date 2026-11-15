import io, os, re, collections
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
keys = sorted(set(re.findall(r'"((?:Auth|Tasks|Monitor|Settings|Proxies|Profiles|Accounts|Analytics|Billing|Home|Checkout|SmartActions|Captcha|Release|Data)\.[\w.]+)":\s*"', raw)))
print('locale keys in the image:', len(keys))
used = set()
for dp, _d, fns in os.walk(r'D:\projects\cyber-reverse\replica\src'):
    for fn in fns:
        if fn.endswith('.cs'):
            t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
            for k in keys:
                if k in t: used.add(k)
missing = [k for k in keys if k not in used]
print('referenced by the replica:', len(used))
print('NOT referenced:', len(missing))
per = collections.Counter(k.split('.')[0] for k in missing)
print('by area:', dict(per))
print()
for k in missing[:20]: print('   ', k)
