import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# introduce the fingerprint right after the profile directory is known
old = '''        var profile = profilePath ?? Path.Combine(Path.GetTempPath(),
            "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(profile);'''

new = '''        var profile = profilePath ?? Path.Combine(Path.GetTempPath(),
            "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(profile);

        // R130: one fingerprint per profile, derived from the profile key. Stable for the life of the
        // profile, different from every other profile — which is the point of the image's
        // Fingerprint.template.json and its numbered profile folders.
        var fingerprint = BrowserFingerprint.ForProfile(profile);'''

if old not in t:
    raise SystemExit("profile anchor missing")
t = t.replace(old, new, 1)

# resolve the two placeholders in the injected script
old_ph = '''              Object.defineProperty(N, 'hardwareConcurrency', { get: () => __HC__, configurable: true });
              Object.defineProperty(N, 'deviceMemory', { get: () => __DM__, configurable: true });'''
new_ph = '''              Object.defineProperty(N, 'hardwareConcurrency', { get: () => ''' + "''' + ''' + ''' + ''' + ''' + ''' + ''' + ''','''

# simpler: build the replacement with explicit values substituted at runtime via string.Format-free concat
new_ph = (
    "              Object.defineProperty(N, 'hardwareConcurrency', { get: () => \" +\n"
    "                fingerprint.HardwareConcurrency + @\", configurable: true });\n"
    "              Object.defineProperty(N, 'deviceMemory', { get: () => \" +\n"
    "                fingerprint.DeviceMemory + @\", configurable: true });"
)
if old_ph not in t:
    raise SystemExit("placeholder anchor missing")
t = t.replace(old_ph, new_ph, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fingerprint resolved into the injected script")
