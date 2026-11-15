import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()
start = t.index('public sealed class WebhookCreatorView')
seg = t[start:]
idx = seg.index('BuildFooter(SaveButton(')
print(seg[max(0,idx-700):idx+80])
