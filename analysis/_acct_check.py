import io, os, re
raw = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"(Accounts\.[\w.]+)":\s*"([^"\n]{1,90})"', raw)))
txt = ''.join(io.open(os.path.join(dp, f), encoding='utf-8', errors='replace').read()
              for dp, _d, fs in os.walk(r'D:\projects\cyber-reverse\replica\src') for f in fs if f.endswith('.cs'))
missing = [(k, v) for k, v in pairs if v not in txt]
print('Accounts keys:', len(pairs), 'missing:', len(missing))
for k, v in missing:
    print('  ', k, '=', repr(v))
