import io, os, glob, json
A = os.path.expandvars(r"%APPDATA%\Cybersole")
p = sorted(glob.glob(os.path.join(A,'Backups','*.cyb')))[-1]
d = json.loads(io.open(p, encoding='utf-8', errors='replace').read())['settings']
for k in ('clock','currency','scrollbarWidth','language','keybinds','notifications','smartactions','startup','pinGroups'):
    print('%-16s %s' % (k, str(d.get(k))[:40]))
print()
print('has enableClock:', 'enableClock' in d, '| has clockFormat:', 'clockFormat' in d, '| has monitorConcurrency:', 'monitorConcurrency' in d, '| has storeGroups:', 'storeGroups' in d)
