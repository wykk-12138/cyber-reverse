import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for k, v in sorted(set(re.findall(r'"(Settings\.Aycd\.[\w.]+)":\s*"([^"]{0,50})"', raw))):
    print('   %-42s %s' % (k, v))
