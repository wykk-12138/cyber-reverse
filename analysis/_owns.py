import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs'
t = io.open(p, encoding='utf-8').read()

# declare the ownership flag next to ProfilePath
old = '    public string ProfilePath { get; private set; } = string.Empty;'
new = '''    public string ProfilePath { get; private set; } = string.Empty;

    /// <summary>True when this bridge minted the temp profile, so disposing it may delete the directory.</summary>
    private bool _ownsProfile;'''
assert old in t
t = t.replace(old, new, 1)

# set it where the profile is resolved
old2 = '''        var profile = profilePath ?? Path.Combine(Path.GetTempPath(),
            "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(profile);'''
new2 = '''        var ownsProfile = string.IsNullOrWhiteSpace(profilePath);
        var profile = ownsProfile
            ? Path.Combine(Path.GetTempPath(), "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8])
            : profilePath!;
        Directory.CreateDirectory(profile);'''
assert old2 in t
t = t.replace(old2, new2, 1)

# and where ProfilePath is assigned
old3 = '        bridge.ProfilePath = profile;'
new3 = '        bridge.ProfilePath = profile;\n        bridge._ownsProfile = ownsProfile;'
assert old3 in t
t = t.replace(old3, new3, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ownership flag wired')
