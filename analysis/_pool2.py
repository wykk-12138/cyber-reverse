import io
pool = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read()
for k in ['CheckForUpdates','check for updates','Check for updates','Quicktask','QuickTask','Quicks','Settings.Version','General.Language','MonitorConcurrency','StartupPage','TimeRemaining','Settings.General']:
    print('%-24s %s' % (k, 'IN POOL' if k in pool else '-'))
