import io, os
R = r'D:\projects\cyber-reverse\replica'
CRLF = b"\r\n"
pairs = [
 ('tools/.mutation-backup/PARITY.md', 'docs/PARITY.md'),
 ('tools/.mutation-backup/ChromiumBridge.cs', 'src/Cybersole.Stores/Scripts/ChromiumBridge.cs'),
 ('tools/.mutation-backup/ShopifyFlow.cs', 'src/Cybersole.Stores/Flows/ShopifyFlow.cs'),
 ('tools/.mutation-backup/SettingsViews.cs', 'src/Cybersole.Ui/Views/Settings/SettingsViews.cs'),
]
for b, l in pairs:
    bb = io.open(os.path.join(R, b), 'rb').read()
    ll = io.open(os.path.join(R, l), 'rb').read()
    print('%-52s identical=%s  bak=%dB(crlf %d)  live=%dB(crlf %d)' % (l, bb == ll, len(bb), bb.count(CRLF), len(ll), ll.count(CRLF)))
