import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumKasadaSolver.cs"
t = io.open(p, encoding="utf-8").read()

# 1) SolveAsync takes the session so the identity can be recorded where the token is produced
old = '''    public async Task<KasadaResult> SolveAsync(string pageUrl, TimeSpan? timeout = null,
        string? triggerUrl = null, CancellationToken ct = default)
    {'''

new = '''    public async Task<KasadaResult> SolveAsync(string pageUrl, TimeSpan? timeout = null,
        string? triggerUrl = null, CancellationToken ct = default, FlowSession? session = null)
    {'''

if old not in t:
    raise SystemExit("SolveAsync anchor missing")
t = t.replace(old, new, 1)

# 2) record the identity immediately after launch, before the page is touched
old2 = '''            bridge = await ChromiumBridge.LaunchAsync(ct: ct).ConfigureAwait(false);'''
new2 = '''            bridge = await ChromiumBridge.LaunchAsync(ct: ct).ConfigureAwait(false);

            // R135: the browser that solves this token is the browser the payment will describe. One
            // key, recorded here, so the profile folder, the fingerprint and the 3-D Secure profile all
            // belong to the same machine.
            if (session is not null)
            {
                BrowserIdentity.RecordProfile(session, bridge.ProfilePath,
                    utcOffsetMinutes: BrowserIdentity.TimeZoneOffset(session),
                    userAgentAlreadySent: true);
            }'''

if old2 not in t:
    raise SystemExit("launch anchor missing")
t = t.replace(old2, new2, 1)

# 3) the result carries the key for callers that have no session
old3 = '''    public string? ScriptUrl { get; private set; }'''
new3 = '''    public string? ScriptUrl { get; private set; }

    /// <summary>
    /// The profile key this token was produced on — the identity the payment must describe.
    /// Empty when the run never reached a browser.
    /// </summary>
    public string ProfileKey { get; private set; } = string.Empty;'''

if old3 not in t:
    raise SystemExit("ScriptUrl anchor missing")
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("solver records and returns the profile key")
