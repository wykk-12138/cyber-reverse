import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for k, v in sorted(set(re.findall(r'"(Utilities\.StoreGroups\.[\w.]+)":\s*"([^"]{0,60})"', raw))):
    print('   %-46s %s' % (k, v))
