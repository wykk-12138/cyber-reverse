import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# expose the two facts a caller needs to keep identities aligned
old = '''    private ChromiumBridge(Process process, ClientWebSocket socket, HttpClient http, int port)'''

new = '''    /// <summary>
    /// The user-data-dir this instance launched with — also the key its fingerprint is derived from.
    ///
    /// <para>
    /// R135: callers need it to record the same identity in the session, so the browser that solved a
    /// token and the payment that later reports a screen are provably the same machine.
    /// </para>
    /// </summary>
    public string ProfilePath { get; private set; } = string.Empty;

    /// <summary>The fingerprint this launch uses.</summary>
    public BrowserFingerprint Fingerprint { get; private set; } = BrowserFingerprint.ForProfile("unknown");

    private ChromiumBridge(Process process, ClientWebSocket socket, HttpClient http, int port)'''

if old not in t:
    raise SystemExit("ctor anchor missing")
t = t.replace(old, new, 1)

# set them where the fingerprint is derived
old2 = '''        var fingerprint = BrowserFingerprint.ForProfile(profile);'''
new2 = '''        var fingerprint = BrowserFingerprint.ForProfile(profile);'''
if old2 not in t:
    raise SystemExit("fingerprint anchor missing")

# after the instance is created and returned, assign both; find "return bridge;"
old3 = '''        return bridge;'''
new3 = '''        bridge.ProfilePath = profile;
        bridge.Fingerprint = fingerprint;

        return bridge;'''
if old3 not in t:
    raise SystemExit("return anchor missing")
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge exposes ProfilePath and Fingerprint")
