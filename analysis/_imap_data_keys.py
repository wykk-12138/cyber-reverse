import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for prefix in ('Settings.Imap', 'Settings.Data', 'Settings.Payment'):
    keys = sorted(set(re.findall(r'"(' + prefix + r'\.[\w.]+)":\s*"([^"]{0,50})"', raw)))
    print('== ' + prefix, len(keys))
    for k, v in keys[:12]:
        print('    %-46s %s' % (k, v))
