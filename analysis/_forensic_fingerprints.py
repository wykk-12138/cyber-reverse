import io, os, glob, json, re
A = os.path.expandvars(r"%APPDATA%\Cybersole")

def fingerprint(path):
    raw = io.open(path, 'rb').read()
    head = raw[:120].decode('utf-8', 'replace')
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n') - crlf
    indent = re.match(r'\[?\{?\r?\n(\s+)', head)
    case = 'Pascal' if re.search(r'"[A-Z][a-zA-Z]*"\s*:', head) else ('camel' if re.search(r'"[a-z][a-zA-Z]*"\s*:', head) else '?')
    spaced = bool(re.search(r'"\s*:\s', head))
    return dict(bytes=len(raw), crlf=crlf, lf=lf, indent=len(indent.group(1)) if indent else 0,
                case=case, space_after_colon=spaced, head=head[:60].replace('\r', '\\r').replace('\n', '\\n'))

files = ['settings.json', 'tasks.json', 'solvers.json', 'accounts.json', 'billing.json',
         'proxies.json', 'analytics.json', 'smartActions.json', 'smartActionUtilities.json',
         'checkoutHistory.json', 'sessions.json']
for fn in files:
    p = os.path.join(A, fn)
    if not os.path.exists(p) or os.path.getsize(p) < 3:
        print('%-26s (empty or missing)' % fn)
        continue
    f = fingerprint(p)
    print('%-26s %6d B  crlf=%-4d lf=%-3d indent=%d case=%-6s space=%s' % (fn, f['bytes'], f['crlf'], f['lf'], f['indent'], f['case'], f['space_after_colon']))
print()
for p in sorted(glob.glob(os.path.join(A, 'Backups', '*.cyb')))[:2]:
    f = fingerprint(p)
    print('%-26s %6d B  crlf=%-4d lf=%-3d indent=%d case=%-6s space=%s' % (os.path.basename(p), f['bytes'], f['crlf'], f['lf'], f['indent'], f['case'], f['space_after_colon']))
    print('     head:', f['head'])
