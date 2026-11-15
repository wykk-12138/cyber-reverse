import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"(ProfileCsv\.[\w.]+)":\s*"([^"\n]{1,80})"', raw)))
print(len(pairs))
for k, v in pairs: print('%s\t%s' % (k, v))
