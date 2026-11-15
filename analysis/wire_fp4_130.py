import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) declare the fingerprint next to the profile directory
old = '''        var profile = profilePath ?? Path.Combine(Path.GetTempPath(),
            "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(profile);'''
new = '''        var profile = profilePath ?? Path.Combine(Path.GetTempPath(),
            "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(profile);

        // R130: one fingerprint per profile, derived from the profile key. Stable for the life of the
        // profile and different from every other profile — what the image's Fingerprint.template.json
        // and its numbered profile folders are for.
        var fingerprint = BrowserFingerprint.ForProfile(profile);'''
if old not in t:
    raise SystemExit("profile anchor missing")
t = t.replace(old, new, 1)

# 2) substitute the placeholders where the script is handed to the page
old_src = "                source = StealthScript,"
new_src = ("                source = StealthScript\n"
           "                    .Replace(\"__HC__\", fingerprint.HardwareConcurrency.ToString())\n"
           "                    .Replace(\"__DM__\", fingerprint.DeviceMemory.ToString()),")
if old_src not in t:
    raise SystemExit("injection anchor missing")
t = t.replace(old_src, new_src, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fingerprint declared and substituted")
