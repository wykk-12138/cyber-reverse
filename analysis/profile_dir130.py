import io

# 1) BrowserFingerprint gains the profile-directory name the image uses (Profile 0..8)
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\BrowserFingerprint.cs"
t1 = io.open(p1, encoding="utf-8").read()

anchor = "    /// <summary>The window size argument for this fingerprint's screen.</summary>"
add = '''    /// <summary>
    /// The Chrome profile-directory name, from the numbered folders the image ships
    /// (<c>Profile 0</c>, <c>Profile 1</c>, <c>Profile 6</c>, <c>Profile 8</c>).
    ///
    /// <para>
    /// A persistent user-data-dir holds several <c>Profile N</c> folders, and Chromium is told which
    /// one to use with <c>--profile-directory=</c>. Deriving the number from the profile key keeps one
    /// profile key on one directory across restarts — the folder and the fingerprint then describe the
    /// same identity.
    /// </para>
    /// </summary>
    public string ProfileDirectoryName(string profileKey) =>
        "Profile " + (StableHash(profileKey) % 9);

    /// <summary>The switch Chromium takes for that directory.</summary>
    public string ProfileDirectoryArgument(string profileKey) =>
        "--profile-directory=" + ProfileDirectoryName(profileKey);

    /// <summary>The window size argument for this fingerprint's screen.</summary>'''

if anchor not in t1:
    raise SystemExit("window-size anchor missing")
t1 = t1.replace(anchor, add, 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)
print("profile-directory name added")

# 2) ChromiumBridge passes it for a persistent profile
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t2 = io.open(p2, encoding="utf-8").read()

old = '''            fingerprint.WindowSizeArgument(),'''
new = '''            fingerprint.WindowSizeArgument(),

            // A persistent user-data-dir holds several Profile N folders; a temp one does not need to
            // name any. The number comes from the same key as the fingerprint.
            fingerprint.ProfileDirectoryArgument(profile),'''
if old not in t2:
    raise SystemExit("window arg anchor missing")
t2 = t2.replace(old, new, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("launch args carry --profile-directory")
