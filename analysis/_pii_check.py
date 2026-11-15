import io, os, json, re
A = os.path.expandvars(r"%APPDATA%\Cybersole")
for fn in ('settings.json','tasks.json'):
    raw = io.open(os.path.join(A, fn), encoding='utf-8-sig', errors='replace').read()
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', raw)
    print(fn, 'emails found:', sorted(set(emails))[:5])
    names = re.findall(r'"name"\s*:\s*"([^"]{0,40})"', raw)
    print('   names:', names[:6])
