import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
want = ['Quicks', 'Settings.Version', 'CheckForUpdates', 'Settings.General.', 'TimeRemaining', 'MonitorConcurrency', 'StartupPage', 'General.Language']
for ln in lines:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if any(w in t for w in want):
        print(m.group(1), t[:200])
