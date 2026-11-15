import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
fam = sorted(set(re.findall(r'"([A-Z][\w.]*\.(?:Loaded\w*|CountFormat|CountOne|CountNone|GroupsLoaded\w*|Selected\w*))":', raw)))
print('caption keys:', len(fam))
for k in fam: print('   ', k)
