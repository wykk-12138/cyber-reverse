import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AdyenBrowserInfoTests.cs"
t = io.open(p, encoding="utf-8").read()

# R134 moved the reads behind BrowserIdentity, so the R133 assertions name the new collaborator.
old = '''        Assert.Contains("BrowserFingerprint.ForProfile(", text);
        Assert.Contains("DlpaProfile.From(fingerprint", text);'''

new = '''        Assert.Contains("BrowserIdentity.Fingerprint(c.Session)", text);
        Assert.Contains("DlpaProfile.From(fingerprint", text);'''

if old not in t:
    raise SystemExit("derived anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("R133 assertions follow the R134 indirection")
