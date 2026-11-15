import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\SettingsDialogSingleSourceTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("settings.CustomStores ??= new List<CustomStore>()", source);'''
new = '''        Assert.Contains("Settings.CustomStores ??= new List<CustomStore>()", source);'''
if old not in t:
    raise SystemExit("store write anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("anchor corrected")
