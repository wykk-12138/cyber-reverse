import io
# 1) SmartActionsView's "View logs" -> "View Logs" (Settings.Data.ViewLogs)
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t1 = io.open(p1, encoding='utf-8').read()
assert 'UiKit.Button("View logs"' in t1
t1 = t1.replace('UiKit.Button("View logs"', 'UiKit.Button("View Logs"', 1)
io.open(p1, 'w', encoding='utf-8', newline='').write(t1)
print('View logs -> View Logs')

# 2) Custom sizes add button: "Add Size(s)" -> "Add Size"
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t2 = io.open(p2, encoding='utf-8').read()
assert '"Add Size(s)"' in t2
t2 = t2.replace('UiKit.Button("Add Size(s)"', 'UiKit.Button("Add Size"', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('Add Size(s) -> Add Size')

# 3) the cloudflare-solvers empty subtitle: use its own sentence, not the proxies one
t2 = io.open(p2, encoding='utf-8').read()
old = 'var empty = UiKit.Empty(EmptyView.Headline);'
idx = t2.index('public sealed class CloudflareSolversView')
seg = t2[idx:idx + 900]
if old in seg:
    t2 = t2[:idx] + seg.replace(old, 'var empty = UiKit.Empty(EmptyView.Headline, "Add a Cloudflare provider to get started");', 1) + t2[idx + 900:]
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('cloudflare empty subtitle fixed')
else:
    print('cloudflare empty state not found in that window')
