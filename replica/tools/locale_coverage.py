import io, os, re, collections, sys

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
SRC = r'D:\projects\cyber-reverse\replica\src'
AREAS = ('Auth','Tasks','Monitor','Settings','Proxies','Profiles','Accounts','Analytics','Billing','Home','Checkout','SmartActions','Captcha','Release','Data','GroupModal','TaskGroup','TaskCreator','HistoryWindow')

def keys(path=POOL):
    raw = io.open(path, encoding='utf-8', errors='replace').read()
    pat = r'"((?:' + '|'.join(AREAS) + r')\.[\w.]+)":\s*"'
    return sorted(set(re.findall(pat, raw)))

def used(key_set):
    hit = set()
    for dp, _d, fns in os.walk(SRC):
        for fn in fns:
            if fn.endswith('.cs'):
                t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
                for k in key_set:
                    if k in t:
                        hit.add(k)
    return hit

all_keys = keys()
hit = used(all_keys)
missing = [k for k in all_keys if k not in hit]

area = sys.argv[1] if len(sys.argv) > 1 else None
print('locale keys: %d | referenced: %d | not referenced: %d (%.0f%% covered)'
      % (len(all_keys), len(hit), len(missing), 100.0 * len(hit) / max(1, len(all_keys))))
per = collections.Counter(k.split('.')[0] for k in missing)
print('unreferenced by area: ' + ', '.join('%s %d' % (a, n) for a, n in per.most_common()))
if area:
    print()
    for k in missing:
        if k.split('.')[0].lower() == area.lower():
            print('   ', k)
