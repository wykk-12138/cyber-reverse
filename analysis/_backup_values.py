import io, os, glob, json
A = os.path.expandvars(r"%APPDATA%\Cybersole")
p = sorted(glob.glob(os.path.join(A,'Backups','*.cyb')))[-1]
d = json.loads(io.open(p, encoding='utf-8', errors='replace').read())
g = d['tasks'][0]
print('task group sample:', {k: (str(v)[:40]) for k, v in g.items() if k not in ('webhooks','tasks')})
print()
pr = d['proxies'][0]
print('proxy group sample:', {k: (str(v)[:40]) for k, v in pr.items() if k != 'proxies'})
if pr.get('proxies'):
    print('proxy entry keys:', list(pr['proxies'][0].keys()))
print()
sv = d['solvers'][0]
print('solver doc sample:', {k: (str(v)[:30]) for k, v in sv.items() if k != 'solvers'})
if sv.get('solvers'):
    print('solver entry keys:', list(sv['solvers'][0].keys()))
print()
st = d['settings']
print('settings keys count:', len(st))
for k in ('bearer','license','quickTaskProxies','shopifyBrowserProxy','browserPath','currency','clockFormat','maxLogRetention','backupInterval'):
    if k in st: print('   %-22s %s' % (k, str(st[k])[:30]))
