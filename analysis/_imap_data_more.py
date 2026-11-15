import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
keys = sorted(set(re.findall(r'"(Settings\.Imap\.[\w.]+)":\s*"([^"]{0,50})"', raw)))
for k, v in keys[10:]: print('    %-46s %s' % (k, v))
print()
dk = sorted(set(re.findall(r'"(Settings\.Data\.[\w.]+)":\s*"([^"]{0,50})"', raw)))
for k, v in dk[8:]: print('    %-46s %s' % (k, v))
