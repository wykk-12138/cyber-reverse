import io

# 1) the fingerprint can size itself for a phone profile
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\BrowserFingerprint.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''    public string WindowSizeArgument() => $"--window-size={ScreenWidth - 120},{ScreenHeight - 200}";'''

new1 = '''    public string WindowSizeArgument() => $"--window-size={ScreenWidth - 120},{ScreenHeight - 200}";

    /// <summary>
    /// The launch size that matches the profile's claim.
    ///
    /// <para>
    /// R150: an Apple profile says its screen is 402×874 and its outer window is 402×874. Launching the
    /// browser at the desktop size instead makes <c>outerHeight</c> report the host's height, which the
    /// image's own comment calls out as the worse of two impossibilities — "the host window must actually
    /// be this size or clicks land outside the viewport we claim". So the launch size follows the user
    /// agent the profile will send.
    /// </para>
    /// </summary>
    public string WindowSizeArgument(string? userAgent) =>
        MobileSurface.IsAppleUserAgent(userAgent)
            ? $"--window-size={MobileSurface.ScreenWidth},{MobileSurface.ScreenHeight}"
            : WindowSizeArgument();'''

if old1 not in t1:
    raise SystemExit("window anchor missing")
t1 = t1.replace(old1, new1, 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) LaunchAsync takes the agent it will be asked to claim
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''    public static async Task<ChromiumBridge> LaunchAsync(string? executable = null, int port = 0,
        bool headed = false, string? profilePath = null, CancellationToken ct = default)'''

new2 = '''    public static async Task<ChromiumBridge> LaunchAsync(string? executable = null, int port = 0,
        bool headed = false, string? profilePath = null, CancellationToken ct = default,
        string? userAgent = null)'''

if old2 not in t2:
    raise SystemExit("launch signature anchor missing")
t2 = t2.replace(old2, new2, 1)

old3 = '''            fingerprint.WindowSizeArgument(),'''
new3 = '''            fingerprint.WindowSizeArgument(userAgent),'''
if old3 not in t2:
    raise SystemExit("window argument call anchor missing")
t2 = t2.replace(old3, new3, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("the launch size follows the agent the profile will claim")
