import io, re
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs"
t = io.open(p, encoding='utf-8').read()
m = re.search(r'class GlobalSettings\b', t)
i = t.index('{', m.end()); depth = 0
for j in range(i, len(t)):
    if t[j] == '{': depth += 1
    elif t[j] == '}':
        depth -= 1
        if depth == 0:
            body = t[i:j]; break
props = sorted(set(re.findall(r'public\s+[\w<>,\[\]\?\.]+\s+(\w+)\s*(?:\{\s*get|=>)', body)))
live = """bearer, license, quickTaskProxies, quickTaskProfiles, monitorDelay, retryDelay, timeout, shopifyBrowserProxy, autoOpen3DS, autoOpen3DSLimit, browserPath, browserLimit, browserWindowMode, browserProfiles, browserProfileAssignment, pinGroups, startup, keybinds, notifications, clock, currency, concurrency, maxLogRetention, maxLogSize, backupInterval, maxBackups, smartactions, betaUpdates, taskGroupOrder, proxyGroupOrder, profileGroupOrder, queuePresentation, captchaProviders, cloudflareSolvers, webhooks, notificationOptions, keyBinds, customStores, customSizes, monitorFilters, scrollbarWidth, scrollbarColor, scrollbarCornerRadius, language""".replace('\n','').split(', ')
live = [x.strip() for x in live if x.strip()]
low = {p.lower(): p for p in props}
missing = [k for k in live if k.lower() not in low]
print('trusted live keys:', len(live), '| replica props:', len(props))
print('MISSING in replica:', missing if missing else 'none')
extra = [p for p in props if p.lower() not in {k.lower() for k in live}]
print('EXTRA in replica:', extra)
