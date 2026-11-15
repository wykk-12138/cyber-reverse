import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for k, v in sorted(set(re.findall(r'"(Proxies\.(?:Loaded|Selected)[\w.]*)":\s*"([^"]{0,40})"', raw))):
    print('   %-30s %s' % (k, v))
print()
for k, v in sorted(set(re.findall(r'"(Accounts\.(?:Loaded|GroupsLoaded)[\w.]*)":\s*"([^"]{0,40})"', raw))):
    print('   %-30s %s' % (k, v))
