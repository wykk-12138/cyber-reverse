import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        new SettingsSection("payment", "Payment", s => new PaymentView(s)),
        new SettingsSection("help", "Need Help?", s => new HelpView(s)),'''
new = '''        new SettingsSection("payment", "Payment", s => new PaymentView(s)),
        // R300: the image names sixteen settings sections (Settings.Nav.*); the shell had fifteen — Advanced was
        // missing even though AdvancedView existed. Its position among the others is not evidenced, so it sits before
        // Need Help? as the least surprising place.
        new SettingsSection("advanced", "Advanced", s => new AdvancedView(s)),
        new SettingsSection("help", "Need Help?", s => new HelpView(s)),'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('Advanced section added to the shell')
