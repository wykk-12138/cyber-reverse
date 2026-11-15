import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
want = ['Common.Selected','ProfileCsv.Menu.SelectedCells','Settings.CustomSizes.CountFormat','Settings.CustomStores.CountFormat','SmartActions.Filters.CountFormat','TaskCreator.Proxies.CountFormat','Tasks.CountFormat','Utilities.StoreGroups.CountFormat','Accounts.GroupsLoadedFormat','Accounts.GroupsLoadedOne']
for k in want:
    m = re.search(r'"' + re.escape(k) + r'":\s*"([^"]{0,44})"', raw)
    print('%-42s %s' % (k, m.group(1) if m else '(multi-line)'))
