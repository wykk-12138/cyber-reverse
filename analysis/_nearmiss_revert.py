import io
# revert: the live page was MEASURED as "Add Size(s)"; the locale key may name a different button
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t2 = io.open(p2, encoding='utf-8').read()
if 'UiKit.Button("Add Size",' in t2:
    t2 = t2.replace('UiKit.Button("Add Size",', 'UiKit.Button("Add Size(s)",', 1)
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('Add Size -> Add Size(s) (reverted: the page was measured with the (s))')

# revert: Settings.Data.ViewLogs belongs to the Data page; the SmartActions button is a different surface
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t1 = io.open(p1, encoding='utf-8').read()
if 'UiKit.Button("View Logs"' in t1:
    t1 = t1.replace('UiKit.Button("View Logs"', 'UiKit.Button("View logs"', 1)
    io.open(p1, 'w', encoding='utf-8', newline='').write(t1)
    print('View Logs -> View logs (reverted: placement unverified)')
