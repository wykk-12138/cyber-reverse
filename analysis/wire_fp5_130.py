import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public async Task ApplyStealthAsync(string? userAgent = null, CancellationToken ct = default)
    {
        userAgent ??= DefaultUserAgent();'''

new = '''    public async Task ApplyStealthAsync(string? userAgent = null, CancellationToken ct = default,
        BrowserFingerprint? fingerprint = null)
    {
        userAgent ??= DefaultUserAgent();

        // R130: the hardware hints belong to a profile, not to the build. When no profile is supplied
        // (a probe, a test) one is derived from the UA so the values are still consistent run to run.
        fingerprint ??= BrowserFingerprint.ForProfile(userAgent);'''

if old not in t:
    raise SystemExit("ApplyStealthAsync anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("ApplyStealthAsync takes an optional fingerprint")
