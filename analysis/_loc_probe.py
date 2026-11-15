import io, json, re
p = 'embedded_locale.json'
d = json.load(io.open(p, encoding='utf-8'))
print('keys:', len(d))
groups = {}
for k in d:
    pre = k.split('.')[0]
    groups[pre] = groups.get(pre, 0) + 1
for k, v in sorted(groups.items(), key=lambda kv: -kv[1])[:14]:
    print('%4d  %s' % (v, k))
print('--- 可能属于 splash / login / browser 的键 ---')
for k, v in sorted(d.items()):
    if re.search(r'splash|login|licen[cs]e|browser', k, re.I):
        print('%-46s %s' % (k, str(v)[:70]))
