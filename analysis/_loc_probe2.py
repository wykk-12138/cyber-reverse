import io, re
text = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json', encoding='utf-8').read()
# the replica's locale is the extracted one; count keys and list splash/login/browser ones
keys = re.findall(r'"([A-Za-z0-9_.]+)"\s*:\s*"', text)
print('replica locale keys:', len(keys))
groups = {}
for k in keys:
    groups[k.split('.')[0]] = groups.get(k.split('.')[0], 0) + 1
for k, v in sorted(groups.items(), key=lambda kv: -kv[1])[:12]:
    print('%4d  %s' % (v, k))
print('--- splash / login / license / browser ---')
for k in sorted(set(keys)):
    if re.search(r'splash|login|licen[cs]e|browser|startup', k, re.I):
        print('  ', k)
