import io, re, glob
# for each structural type, is there any name evidence in the pool beyond the member names themselves?
needles = {
 'ProfileCsvRow': ['ProfileCsvRow'], 'FilterRow': ['FilterRow'], 'ActionRow': ['ActionRow'],
 'ComboBoxEdit': ['ComboBoxEdit'], 'Store': ['ColorSupport'], 'LocalizeSwitchExtension': ['LocalizeSwitch'],
 'LocalizeFormatExtension': ['LocalizeFormat'], 'AccountStoreEntry': ['AccountStoreEntry'],
 'AuthWindow': ['AuthWindow'], 'LicenseControl': ['LicenseControl'], 'User': ['IsStaff'],
 'ElementCell': ['ElementCell'], 'AycdInboxAccount': ['AycdInboxAccount'], 'NotificationSound': ['SoundLocation'],
 'BrowserProfile': ['BrowserProfile'], 'SettingsView': ['Transition'], 'IWebhook': ['ExtraFields'],
 'Filter': ['Variable'], 'InputRow': ['InputRow'], 'FilterInputEntry': ['FilterInputEntry'],
 'Platform': ['QuantityAutoAdjustSupport'],
}
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pool = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
for t, keys in needles.items():
    hit = []
    for k in keys:
        hit += [p for p in pool if k in p][:2]
    print('%-22s %s' % (t, ('; '.join(h[:60] for h in hit[:2]) if hit else '— 池子里没有该类型名')))
