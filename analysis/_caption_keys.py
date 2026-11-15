import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
fam = sorted(set(re.findall(r'"([A-Z][\w.]*\.(?:Loaded\w*|CountFormat|CountOne|CountNone|AccountsFormat|AccountsOne))":\s*"([^"]{0,44})"', raw)))
print('caption keys in the image:', len(fam))
for k, v in fam:
    print('   %-42s %s' % (k, v))
