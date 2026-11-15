import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for needle in ('Clock', 'Export', 'Logs', 'Sitelist', 'Configure', 'Clone'):
    hits = sorted(set(re.findall(r'"([\w.]*' + needle + r'[\w.]*)":\s*"([^"]{0,60})"', raw)))
    print('== %-10s %d' % (needle, len(hits)))
    for k, v in hits[:6]:
        print('    %-42s %s' % (k, v))
