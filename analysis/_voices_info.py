import io, json, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
body = io.open(r'D:\projects\cyber-reverse\analysis\_voices.txt', encoding='utf-8').read()
v = json.loads(body)
print('voices', len(v))
print('defaults', sum(1 for r in v if r.get('default')))
print('local', sum(1 for r in v if r.get('localService')))
pref = {}
for r in v:
    p = r['voiceURI'].split('.')[0] + '.' + (r['voiceURI'].split('.')[1] if '.' in r['voiceURI'] else '')
    pref[p] = pref.get(p, 0) + 1
print('uri prefixes', pref)
print('non-apple', [r['voiceURI'] for r in v if not r['voiceURI'].startswith('com.apple')][:5])
print('langs', sorted(set(r['lang'] for r in v))[:8], '...count', len(set(r['lang'] for r in v)))
