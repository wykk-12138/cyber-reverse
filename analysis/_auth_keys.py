import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
keys = sorted(set(re.findall(r'"(Auth\.Login\.[\w.]+)":\s*"([^"]{0,70})"', raw)))
print('Auth.Login keys:', len(keys))
for k, v in keys: print('    %-34s %s' % (k, v))
wk = sorted(set(re.findall(r'"(Auth\.Welcome[^"]*)":\s*"([^"]{0,70})"', raw)))
print('welcome:', wk)
