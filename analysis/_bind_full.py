import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
want = ['ProfileCsvRow','FilterRow','ActionRow','InputRow','FilterInputEntry','ComboBoxEdit','AccountStoreEntry',
        'LocalizeSwitchExtension','LocalizeFormatExtension','ElementCell','AycdInboxAccount','NotificationSound',
        'BrowserProfile','AuthWindow','LicenseControl','Platform','Store','User','IWebhook','Filter','SettingsView']
# d shape: {Type: [members]} or list; inspect
if isinstance(d, dict):
    keys = list(d.keys())[:3]
    print('sample keys:', keys)
    for w in want:
        hits = [k for k in d if w in k]
        if hits:
            print('%-22s %s  (%d 成员)' % (w, hits[0], len(d[hits[0]])))
        else:
            print('%-22s —' % w)
else:
    print(type(d), len(d))
