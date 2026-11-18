using System.Diagnostics;
using System.Net.Http;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Minimal Chrome DevTools Protocol client.
///
/// R18: the R17 finding was that Kasada's payload cannot finish inside a bare JS engine — the
/// original gets away with "local generation" because it ships DotNetBrowser/Chromium. This
/// bridge gives the replica the same thing without a NuGet dependency: launch the Chrome or
/// Edge already installed on the machine, drive it over CDP, and let the page run its own
/// anti-bot script in a real browser.
/// </summary>
public sealed class ChromiumBridge : IAsyncDisposable
{
    private readonly Process _process;
    private readonly ClientWebSocket _socket;
    private readonly HttpClient _http;
    private readonly int _port;
    private int _nextId = 1;
    private readonly SemaphoreSlim _gate = new(1, 1);

    /// <summary>Events the page pushed, used for request-header sniffing.</summary>
    public List<JsonElement> Events { get; } = new();

    /// <summary>
    /// The user-data-dir this instance launched with — also the key its fingerprint is derived from.
    ///
    /// <para>
    /// R135: callers need it to record the same identity in the session, so the browser that solved a
    /// token and the payment that later reports a screen are provably the same machine.
    /// </para>
    /// </summary>
    public string ProfilePath { get; private set; } = string.Empty;

    /// <summary>True when this bridge minted the temp profile, so disposing it may delete the directory.</summary>
    private bool _ownsProfile;

    /// <summary>The fingerprint this launch uses.</summary>
    public BrowserFingerprint Fingerprint { get; private set; } = BrowserFingerprint.ForProfile("unknown");

    private ChromiumBridge(Process process, ClientWebSocket socket, HttpClient http, int port)
    {
        _process = process;
        _socket = socket;
        _http = http;
        _port = port;
    }

    /// <summary>
    /// Launch Chromium and attach to its first page.
    ///
    /// Defaults to headless with a throwaway profile, which is what script execution needs.
    /// Pass <paramref name="headed"/> with a <paramref name="profilePath"/> when the target
    /// site bot-detects a fresh headless session — goat.com and scheels.com both 403 the
    /// default launch, and a normal window with a profile on disk is the way past that.
    /// </summary>
    public static async Task<ChromiumBridge> LaunchAsync(string? executable = null, int port = 0,
        bool headed = false, string? profilePath = null, CancellationToken ct = default,
        string? userAgent = null)
    {
        executable ??= FindBrowser()
                      ?? throw new InvalidOperationException(
                          "no Chrome/Edge/WebView2 runtime found on this machine");

        if (port == 0) port = FreePort();

        var ownsProfile = string.IsNullOrWhiteSpace(profilePath);
        var profile = ownsProfile
            ? Path.Combine(Path.GetTempPath(), "cyb-chromium-" + Guid.NewGuid().ToString("N")[..8])
            : profilePath!;
        Directory.CreateDirectory(profile);

        // R130: one fingerprint per profile, derived from the profile key. Stable for the life of the
        // profile and different from every other profile — what the image's Fingerprint.template.json
        // and its numbered profile folders are for.
        var fingerprint = BrowserFingerprint.ForProfile(profile);

        var psi = new ProcessStartInfo
        {
            FileName = executable,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            // a headed run has to be visible; hiding it is what makes it look synthetic
            CreateNoWindow = !headed,
        };

        var args = new List<string>();

        if (!headed)
        {
            args.Add("--headless=new");
            args.Add("--disable-gpu");
        }

        args.AddRange(new[]
        {
            $"--remote-debugging-port={port}",
            $"--user-data-dir={profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
            fingerprint.WindowSizeArgument(userAgent),

            // A persistent user-data-dir holds several Profile N folders; a temp one does not need to
            // name any. The number comes from the same key as the fingerprint.
            fingerprint.ProfileDirectoryArgument(profile),

            // Bot walls that inspect the JS environment look for these three markers first.
            // Offspring is the case that prompted this: its HTML arrives in full (192 KB from
            // NetClient) but the DOM stays at 11 divs / 3298 bytes, meaning its scripts refused
            // to run. These flags remove the most common reasons a script refuses.
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--exclude-switches=enable-automation",
        });

        // A persistent profile should not be told it is under automation; a temp one does not
        // care. Leaving the flag off in headed mode is part of not looking synthetic.
        if (!headed) args.Add("--enable-automation");

        args.Add("about:blank");

        foreach (var arg in args)
        {
            psi.ArgumentList.Add(arg);
        }

        var process = Process.Start(psi)
                      ?? throw new InvalidOperationException("could not start the browser");

        var http = new HttpClient { BaseAddress = new Uri($"http://127.0.0.1:{port}") };

        // Chrome needs a moment before the DevTools endpoint answers.
        string? wsUrl = null;
        for (var attempt = 0; attempt < 60 && wsUrl is null; attempt++)
        {
            ct.ThrowIfCancellationRequested();
            await Task.Delay(150, ct).ConfigureAwait(false);

            try
            {
                var list = await http.GetStringAsync("/json/list", ct).ConfigureAwait(false);
                using var doc = JsonDocument.Parse(list);
                foreach (var target in doc.RootElement.EnumerateArray())
                {
                    if (!target.TryGetProperty("type", out var type) || type.GetString() != "page") continue;
                    if (!target.TryGetProperty("webSocketDebuggerUrl", out var ws)) continue;
                    wsUrl = ws.GetString();
                    if (wsUrl is not null) break;
                }
            }
            catch (Exception)
            {
                // endpoint not up yet
            }
        }

        if (wsUrl is null)
        {
            try { process.Kill(entireProcessTree: true); } catch (Exception) { /* already gone */ }
            http.Dispose();
            throw new InvalidOperationException("chrome DevTools endpoint never became ready");
        }

        var socket = new ClientWebSocket();
        await socket.ConnectAsync(new Uri(wsUrl), ct).ConfigureAwait(false);

        var bridge = new ChromiumBridge(process, socket, http, port);
        await bridge.SendAsync("Page.enable", null, ct).ConfigureAwait(false);
        await bridge.SendAsync("Runtime.enable", null, ct).ConfigureAwait(false);
        await bridge.SendAsync("Network.enable", null, ct).ConfigureAwait(false);
        bridge.ProfilePath = profile;
        bridge._ownsProfile = ownsProfile;
        bridge.Fingerprint = fingerprint;

        return bridge;
    }

    /// <summary>
    /// Make the session look like a normal desktop Chrome: rewrite the UA (which also
    /// rewrites the UA-CH brands), silence the automation flag, and patch the handful of
    /// navigator properties an anti-bot script reads.
    /// </summary>
    public async Task ApplyStealthAsync(string? userAgent = null, CancellationToken ct = default,
        BrowserFingerprint? fingerprint = null)
    {
        userAgent ??= DefaultUserAgent();

        // R130: the hardware hints belong to a profile, not to the build. When no profile is supplied
        // (a probe, a test) one is derived from the UA so the values are still consistent run to run.
        fingerprint ??= BrowserFingerprint.ForProfile(userAgent);

        // Round 138. This was hardcoded to "131.0.0.0" while DefaultUserAgent() reported the real
        // installed build, so the same session answered two different Chrome versions:
        //
        //   navigator.userAgent                 → Chrome/157.0.8103.38
        //   navigator.userAgentData.brands      → [{ brand: "Google Chrome", version: "131" }]
        //   navigator.userAgentData.fullVersion → "131.0.0.0"
        //
        // A single comparison of those two is enough to reject a session, and it costs a detector
        // nothing. Both now come from the same reading of the installed binary.
        var fullVersion = ChromiumBridgeVersion();          // 157.0.8103.38
        var major = fullVersion.Split('.')[0];              // 157

        // Chrome freezes the UA to <major>.0.0.0 (User-Agent Reduction); the full build only
        // appears in getHighEntropyValues. Reporting the build number in the UA is itself a tell.
        var reducedVersion = major + ".0.0.0";

        await SendAsync("Emulation.setUserAgentOverride", new
        {
            userAgent,
            acceptLanguage = "en-US,en;q=0.9",
            platform = "Win32",
            userAgentMetadata = new
            {
                brands = new object[]
                {
                    new { brand = "Chromium", version = major },
                    new { brand = "Google Chrome", version = major },
                    new { brand = "Not_A Brand", version = "24" },
                },
                fullVersionList = new object[]
                {
                    new { brand = "Chromium", version = fullVersion },
                    new { brand = "Google Chrome", version = fullVersion },
                    new { brand = "Not_A Brand", version = "24.0.0.0" },
                },
                fullVersion = fullVersion,
                platform = "Windows",
                platformVersion = "15.0.0",
                architecture = "x86",
                model = string.Empty,
                mobile = false,
                bitness = "64",
                wow64 = false,
            },
        }, ct).ConfigureAwait(false);

        await SendAsync("Network.setExtraHTTPHeaders", new
        {
            headers = new Dictionary<string, string>
            {
                ["Accept-Language"] = "en-US,en;q=0.9",
                ["sec-ch-ua-mobile"] = "?0",
                ["sec-ch-ua-platform"] = "\"Windows\"",
            },
        }, ct).ConfigureAwait(false);

        // The two surfaces are corrections of a specific mismatch, so they are installed only when the
        // profile claims the engine they describe. A Chromium build claiming Chromium already tells the
        // truth about WebAssembly, and a desktop profile must not report a phone's screen (R148).
        // The engine block is unconditional: it is what a real Chromium reports (five plugins, the connection
        // quartet, the two flags the image's payload carries), so it is true for every profile. The two
        // gated blocks below it correct a *specific* claim and must not be installed otherwise (R148/R156).
        // The mask runs first: every patch after it can register itself as native (R160).
        // R179: engine parity first among the patches — the error wrappers it installs are what the brand
            // check's ELIDE hook talks to, and the stack format applies to everything constructed after.
            var surfaceBody = NativeRefs.BodyJs() + NativeMask.BodyJs() + EngineParity.BodyJs() + MobileSurface.EngineBodyJs();

        if (MobileSurface.IsAppleUserAgent(userAgent) || WebAssemblySurface.ShouldPatch(userAgent))
        {
            if (WebAssemblySurface.ShouldPatch(userAgent)) surfaceBody += WebAssemblySurface.BodyJs();
            if (MobileSurface.IsAppleUserAgent(userAgent))
            {
                surfaceBody += MobileSurface.BodyJs();

                // R157: the touch surface. `'ontouchstart' in window` is not decoration — the image's own note
                // records a wall gating its worker path on it, paired with the user agent's shape.
                surfaceBody += MobileNavigator.BodyJs(userAgent);

                // R163: and then delete what WebKit never shipped. This runs after the engine block, which is
                // the only order that can work when one of the members to delete is one the engine block just
                // installed for desktop profiles.
                surfaceBody += NavPrune.BodyJs();
                surfaceBody += NavPrune.AudioSessionBodyJs();

                // R170: the two Web Share operations, appended as data properties; and the credentials container as an
                // own non-enumerable property of the instance. Both forward rather than simulate.
                surfaceBody += ForwardingShims.WebShareBodyJs();
                surfaceBody += ForwardingShims.CredentialsBodyJs();

                // R167: the two plain values from the thirteen, on the prototype and masked below. Installed
                // BEFORE the reseat, because each install appends a property to the prototype and would
                // otherwise land after everything the reseat just ordered (measured: 29/50 with the order broken).
                surfaceBody += NavigatorLocks.BodyJs();

                // R173: the four most-probed strings become brand-checked accessors, so a foreign receiver throws the
                // way a real accessor does. Before the reseat, like every other install.
                surfaceBody += AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded);

                // R174: the journal, so a same-origin child realm can be patched by path. Last of the installers and
                // before the reseat: it records what exists, it does not create it.
                surfaceBody += PatchJournal.BodyJs();

                // R165: the recorded order, applied last among the value writers.
                surfaceBody += NavOrder.ReseatBodyJs(NavOrder.Navigator);
            }
        }

        // R180 built a key-order layer and left it unwired: wired wide, `mutation-check.py` hung, because a wrapped
        // `Object.getOwnPropertyNames` sat underneath the replay code a mutation disables. R186 narrowed it to the
        // window, R187 read the target's install site (0x03d1efd4) and moved it above the prunes, and R188 finished the
        // dispatch — the ORDER table and CSS_DECL are KeyOrderRules, carried verbatim out of the binary. The old
        // KeyOrderTable body is gone: it was a second copy that nothing called.

        // R182: the twelve Chrome-for-iOS window names. After every other install — they are globals, and the baseline
        // this reports has to be taken once this script has finished — and before the mask pass.
        surfaceBody += WindowBaseline.BodyJs();

        // R184: the two prunes the replica never had. The global one deletes every window name the device's own list
        // does not carry — which is how `'chrome' in window` stops answering — and the document one removes the eight
        // Blink-only members that make hCaptcha's `spst` answer 1 instead of 0.
        // R185: the window order function, and the baseline it reads — taken after every install, which is why it
        // sits here rather than with the other window work.
        surfaceBody += WindowOrder.BodyJs();

        // R187: the key-order layer's three entry points, installed HERE and not after the prunes. That is where the
        // target installs them — `['getOwnPropertyNames','keys'].forEach(...)` at 0x03d1efd4, then `Reflect.ownKeys`,
        // and only afterwards NAV_PRUNE 0x03d208ca, GLOBAL_PRUNE 0x03d272d4, DOCUMENT_PRUNE 0x03d27858. The prunes can
        // live under a wrapped enumerator because they enumerate through `nativeOwnNames`, captured at 0x03d05776
        // before anything was replaced; R186 moved this below them to dodge an interaction the captured reference
        // removes at the source.
        surfaceBody += WindowOrderWrap.BodyJs();

        // R819: gated on the device claim, like every other body that asserts iPhone facts (R193 states the rule
        // two blocks below: a desktop profile must not inherit iPhone-only globals). Both prunes delete every window
        // name the device's list does not carry, and that list is the captured iPhone's 1062 names -- so running them
        // for a desktop profile removed `chrome`, which a desktop Chrome reports as an object. Measured by
        // ChromiumStealthTests.TheRestOfTheFingerprintLooksOrdinary: every other property in its probe was correct
        // while chrome came back undefined. That test drives a real browser and is excluded from the default suite,
        // which is why the deletion stayed invisible.
        if (MobileSurface.IsAppleUserAgent(userAgent))
        {
            surfaceBody += GlobalPrune.GlobalBodyJs();
            surfaceBody += GlobalPrune.DocumentBodyJs();
        }

        // R189: the interface Blink never shipped. A Safari computed style is a CSSStyleProperties — 1468 accessors on
        // the prototype, numeric indices on the instance — and the proxy around getComputedStyle is what stops `in`,
        // hasOwnProperty and descriptor lookups from contradicting the enumeration R188 already fixed. It runs AFTER
        // the global prune, because `window.CSSStyleProperties` is a name the device's list does not carry and the
        // prune would delete it (target: prune 0x03d272d4, synthesis 0x03d98…).
        surfaceBody += CssStyleProperties.BodyJs();

        // R193: and the globals the device has and Blink never shipped. The window list has been the device's since
        // R192, so every name Blink lacks is currently advertised with nothing behind it -- "listed by
        // getOwnPropertyNames(window), `in` false, descriptor undefined", which is the tell this pass removes.
        // R193: gated on the device claim, like every other body that asserts iPhone facts. A desktop profile must not
        // inherit iPhone-only globals — measured ungated: ``'ontouchstart' in window`` became true on a Windows UA.
        // R194: the canvas read-back. Gated with the rest of the device bodies: the baked pictures are this phone's
        // own renderings, so a desktop profile must keep its own pixels.
        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += CanvasSurface.BodyJs();

        // R195: webgl. The parameters name an Apple GPU, so this is another device body.
        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += WebGlSurface.BodyJs();

        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += GlobalSurface.BodyJs();

        // R196: the event-handler attributes as accessor pairs, after the globals are in place (it skips any name
        // that already exists) and before the baseline snapshot.
        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += HandlerSurface.BodyJs();

        // R197: matchMedia. The recorded answers plus the dimension features evaluated against this persona geometry
        // -- hsw asks the media engine to confirm the screen.* it just read.
        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += MediaQuerySurface.BodyJs();

        // R198: measureText metrics and the media-type verdicts.
        if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += FontMediaSurface.BodyJs();

        // The masking pass goes last: a getter that has not been installed yet cannot be masked (R161).
        surfaceBody += MaskTargets.ApplyJs();

        // R192: and the window baseline after even that — the target re-snapshots as the last statement of the whole
        // IIFE (0x03d99162), so the CSSStyleProperties synthesis installed above is counted as this script's, not as
        // something the page defined. Without it those names land at the END of Object.keys(window), which is the
        // slice hsw sweeps.
        surfaceBody += WindowBaselineSnapshot.BodyJs();

        var surfaceDef = "const applySurface = (realm) => {\n  const G = realm;\n" + surfaceBody +
                         "\n          };";

        var source = StealthScript
            .Replace("__SURFACE_DEF__", surfaceDef)
            .Replace("__SURFACE_CALL__", "applySurface(W);")
            .Replace("__HC__", fingerprint.HardwareConcurrency.ToString())
            .Replace("__DM__", fingerprint.DeviceMemory.ToString())
            .Replace("__VOICES__", VoiceTable.VoicesJs);

        await SendAsync("Page.addScriptToEvaluateOnNewDocument", new
        {
            source,
        }, ct).ConfigureAwait(false);

        _stealthInstalled = true;
    }

    /// <summary>A plain Windows desktop Chrome UA — no HeadlessChrome token anywhere.</summary>
    public static string DefaultUserAgent()
    {
        // Chrome freezes the UA token to <major>.0.0.0 under User-Agent Reduction. Sending the
        // full build number makes the UA disagree with getHighEntropyValues().fullVersion, which
        // is a one-line detection. The reduced form is what a real Chrome 157 sends.
        var major = ChromiumBridgeVersion().Split('.')[0];
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
               $"Chrome/{major}.0.0.0 Safari/537.36";
    }

    /// <summary>
    /// The installed browser's full version, from three sources in order: `--version` output,
    /// the executable's file metadata, then a conservative default.
    ///
    /// Round 138: the second source is new. A hardcoded fallback of "131.0.0.0" on a machine
    /// running 157 makes the UA claim a browser 26 majors old — which is not a subtle signal.
    /// </summary>
    private static string ChromiumBridgeVersion()
    {
        try
        {
            using var process = Process.Start(new ProcessStartInfo
            {
                FileName = FindBrowser()!,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                ArgumentList = { "--version" },
            });

            if (process is not null)
            {
                var text = process.StandardOutput.ReadToEnd();
                process.WaitForExit(2000);
                var m = System.Text.RegularExpressions.Regex.Match(text, @"(\d+\.\d+\.\d+\.\d+)");
                if (m.Success) return m.Groups[1].Value;
            }
        }
        catch (Exception)
        {
            // fall through to the file metadata
        }

        // Second source: the executable's own version resource. This is what Windows shows in
        // Properties → Details, and it is correct even when --version is silent (some builds and
        // some locked-down configurations print nothing).
        try
        {
            var path = FindBrowser();
            if (!string.IsNullOrEmpty(path) && File.Exists(path))
            {
                var info = System.Diagnostics.FileVersionInfo.GetVersionInfo(path);
                var candidate = info.ProductVersion ?? info.FileVersion;
                if (!string.IsNullOrWhiteSpace(candidate))
                {
                    var m = System.Text.RegularExpressions.Regex.Match(candidate, @"(\d+)\.(\d+)\.(\d+)\.(\d+)");
                    if (m.Success) return m.Value;
                }
            }
        }
        catch (Exception)
        {
            // fall through
        }

        // Last resort. Deliberately a version this project has actually run against rather than a
        // number that happens to be old; a stale claim here is worse than no claim.
        return "131.0.0.0";
    }

    /// <summary>
    /// Patches for the properties an anti-bot script reads before trusting a session.
    /// Kept deliberately small: each line here is something a real browser answers
    /// differently from a freshly launched headless one.
    ///
    /// Round 136: every patch is now a function of the realm it applies to, and the whole set is
    /// replayed into same-origin child frames. The reason is in the live build's own comment:
    ///
    ///   "An iframe gets its own constructors, so a same-origin child is otherwise completely
    ///    unspoofed — read iframe.contentWindow.navigator and the real Blink values come
    ///    straight back."
    ///
    /// A detector that wants the truth does not need to defeat these patches; it only needs to
    /// create an iframe and read the child. Until this round the replica answered honestly there.
    /// </summary>
    private const string StealthScript = """
        (() => {
          // Every patch takes the realm it acts on. Nothing here reads a bare `navigator` or
          // `window`, because the same code has to run against a child frame's global.
          __SURFACE_DEF__

          const apply = (W) => {
            const N = W.navigator;
            if (!N) return;


            // 1. webdriver must be absent, not false
            try {
              Object.defineProperty(N, 'webdriver', { get: () => undefined, configurable: true });
            } catch (e) {}

            // 2. window.chrome exists in real Chrome
            try {
              if (!W.chrome) W.chrome = {};
              W.chrome.runtime = W.chrome.runtime || {};
            } catch (e) {}

            // 3. plugins/mimeTypes: LEFT NATIVE (R169). Blink's lists are the spec's five PDF viewers and two mime
            //    types, which is exactly what an iPhone reports and what the device collector reads. A patch here
            //    used to answer three and none, so the earlier replica was further from the device than doing
            //    nothing at all.

            // 4. languages
            try {
              Object.defineProperty(N, 'languages', { get: () => ['en-US', 'en'], configurable: true });
            } catch (e) {}

            // 5. permissions.query must not answer 'denied' for notifications
            try {
              if (N.permissions && N.permissions.query) {
                const original = N.permissions.query.bind(N.permissions);
                N.permissions.query = (parameters) =>
                  parameters && parameters.name === 'notifications'
                    ? Promise.resolve({ state: W.Notification ? W.Notification.permission : 'default', onchange: null })
                    : original(parameters);
              }
            } catch (e) {}

            // 6. a headless GPU reports SwiftShader; a desktop reports a real vendor
            try {
              const ctx = W.WebGLRenderingContext;
              if (ctx && ctx.prototype) {
                const getParameter = ctx.prototype.getParameter;
                ctx.prototype.getParameter = function (p) {
                  if (p === 37445) return 'Intel Inc.';
                  if (p === 37446) return 'Intel Iris OpenGL Engine';
                  return getParameter.call(this, p);
                };
              }
            } catch (e) {}

            // 7. hardware hints
            try {
              // R130: per-profile, not 8/8 for every run — two sessions from one install used to
              // report identical hardware, which is the first thing a fingerprint check looks at.
              Object.defineProperty(N, 'hardwareConcurrency', { get: () => __HC__, configurable: true });
              Object.defineProperty(N, 'deviceMemory', { get: () => __DM__, configurable: true });
              Object.defineProperty(N, 'maxTouchPoints', { get: () => 0, configurable: true });
            } catch (e) {}

            // 8. headless leaves this out; real Chrome sets it
            try {
              Object.defineProperty(W, 'outerWidth', { get: () => W.innerWidth, configurable: true });
              Object.defineProperty(W, 'outerHeight', { get: () => W.innerHeight + 85, configurable: true });
            } catch (e) {}

            // 9. a headless Chrome reports an empty voice list. The live build answers from the
            //    captured device for the same reason:
            //
            //      method(voiceTarget, 'getVoices', function () { return VOICES.slice(); });
            //
            //    An empty getVoices() is one of the cheapest checks there is: no real browser on
            //    any platform ships zero voices, so `speechSynthesis.getVoices().length === 0`
            //    alone is enough to reject a session.
            try {
              // R199: the list was six Windows/Google voices, which is a louder tell than no list at all: the device
              // reports 68 APPLE voices (`com.apple.voice.super-compact.nl-BE.Ellen` and friends), so both the count
              // and every voiceURI disagreed with the persona. The table is VoiceTable, verbatim from the script.
              const voices = __VOICES__.map((v) => Object.freeze(v));

              const target = (W.SpeechSynthesis && W.SpeechSynthesis.prototype
                && typeof W.SpeechSynthesis.prototype.getVoices === 'function')
                ? W.SpeechSynthesis.prototype
                : W.speechSynthesis;

              if (target && typeof target.getVoices === 'function') {
                Object.defineProperty(target, 'getVoices', {
                  configurable: true,
                  writable: true,
                  value: function getVoices() { return voices.slice(); },
                });
              }
            } catch (e) {}

            // Last, so it wins: the engine block restates the members the payload reads (five plugins, the
            // connection quartet, the two flags) and has to run after the individual patches above, which
            // R156's browser measurement showed replacing it when it ran first.
            __SURFACE_CALL__
          };

          // The set of realms already patched. A WeakSet rather than a flag on the window: a
          // frame can be navigated, which replaces its global, and the new one must be patched.
          const PATCHED = new WeakSet();

          const replay = (win) => {
            try {
              if (!win || PATCHED.has(win)) return;
              PATCHED.add(win);
              apply(win);
            } catch (e) {}
          };

          replay(globalThis);

          // ---- realm replay -------------------------------------------------------------
          // Two hooks, because an iframe becomes readable by two different routes and a
          // detector can take either: creating it, or reading contentWindow off one that
          // already exists (which is what ad and fingerprint scripts actually do).
          //
          // The `load` event is NOT enough, and the live build says why:
          //
          //   "a frame created with createElement/appendChild never navigates, so there is no
          //    document-start for the host to hook. Replay the recorded patches instead, at the
          //    moment the page reaches for the child."
          //
          // A src-less iframe is about:blank, which never fires load. So the load hook below is a
          // bonus for frames that do navigate, and the contentWindow getter is what actually
          // covers the common case.

          try {
            const createElement = Document.prototype.createElement;
            Document.prototype.createElement = function (tag) {
              const el = createElement.apply(this, arguments);
              try {
                if (String(tag).toLowerCase() === 'iframe') {
                  // patch at creation too: by the time a caller reads contentWindow the getter
                  // below will run anyway, but this keeps the two routes consistent
                  replay(el.contentWindow);
                  el.addEventListener('load', () => replay(el.contentWindow));
                }
              } catch (e) {}
              return el;
            };
          } catch (e) {}

          try {
            const proto = HTMLIFrameElement.prototype;
            const descriptor = Object.getOwnPropertyDescriptor(proto, 'contentWindow');
            if (descriptor && descriptor.get) {
              const get = descriptor.get;
              Object.defineProperty(proto, 'contentWindow', {
                configurable: true,
                get() {
                  const win = get.call(this);
                  replay(win);
                  return win;
                },
              });
            }
          } catch (e) {}
        })();
        """;

    /// <summary>First browser executable found on this machine.</summary>
    public static string? FindBrowser()
    {
        var candidates = new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                @"Google\Chrome\Application\chrome.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                @"Google\Chrome\Application\chrome.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"Google\Chrome\Application\chrome.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                @"Microsoft\Edge\Application\msedge.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                @"Microsoft\Edge\Application\msedge.exe"),
        };

        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }

        return null;
    }

    private static int FreePort()
    {
        using var listener = new System.Net.Sockets.TcpListener(System.Net.IPAddress.Loopback, 0);
        listener.Start();
        var port = ((System.Net.IPEndPoint)listener.LocalEndpoint).Port;
        listener.Stop();
        return port;
    }

    /// <summary>
    /// Send one CDP command and return its result payload.
    ///
    /// Bounded by <paramref name="timeout"/>, because a navigation can interrupt the socket
    /// mid-flight: the reply never arrives, the read loop blocks forever, and the caller hangs
    /// with no way to tell the difference from a slow page. A timed-out command reports as a
    /// failure instead of wedging the session.
    /// </summary>
    public async Task<JsonElement> SendAsync(string method, object? parameters,
        CancellationToken ct = default, TimeSpan? timeout = null)
    {
        var budget = timeout ?? TimeSpan.FromSeconds(20);
        using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        timeoutCts.CancelAfter(budget);
        var inner = timeoutCts.Token;

        await _gate.WaitAsync(inner).ConfigureAwait(false);
        try
        {
            var id = _nextId++;
            var payload = JsonSerializer.Serialize(new
            {
                id,
                method,
                @params = parameters ?? new { },
            });

            await _socket.SendAsync(Encoding.UTF8.GetBytes(payload), WebSocketMessageType.Text,
                true, inner).ConfigureAwait(false);

            // Read until the reply with our id arrives, collecting events on the way.
            var buffer = new byte[1 << 16];
            var text = new StringBuilder();

            while (true)
            {
                text.Clear();
                WebSocketReceiveResult result;
                do
                {
                    result = await _socket.ReceiveAsync(buffer, inner).ConfigureAwait(false);
                    if (result.MessageType == WebSocketMessageType.Close)
                        throw new InvalidOperationException("devtools socket closed");
                    text.Append(Encoding.UTF8.GetString(buffer, 0, result.Count));
                } while (!result.EndOfMessage);

                using var doc = JsonDocument.Parse(text.ToString());
                var root = doc.RootElement;

                if (root.TryGetProperty("id", out var replyId) && replyId.GetInt32() == id)
                {
                    if (root.TryGetProperty("error", out var error))
                        throw new InvalidOperationException($"CDP {method}: {error}");

                    return root.TryGetProperty("result", out var res)
                        ? res.Clone()
                        : default;
                }

                // a notification (event) — keep it for header sniffing
                Events.Add(root.Clone());
            }
        }
        finally
        {
            _gate.Release();
        }
    }

    /// <summary>
    /// Evaluate an expression in the page and return its string form. Set
    /// <paramref name="awaitPromise"/> for an async probe such as a fetch.
    /// </summary>
    public async Task<string?> EvaluateAsync(string expression, CancellationToken ct = default,
        bool awaitPromise = false)
    {
        var result = await SendAsync("Runtime.evaluate", new
        {
            expression,
            returnByValue = true,
            awaitPromise,
        }, ct).ConfigureAwait(false);

        if (result.ValueKind != JsonValueKind.Object) return null;
        if (!result.TryGetProperty("result", out var remote)) return null;

        if (remote.TryGetProperty("value", out var value))
        {
            return value.ValueKind switch
            {
                JsonValueKind.String => value.GetString(),
                JsonValueKind.Null or JsonValueKind.Undefined => null,
                _ => value.ToString(),
            };
        }

        if (remote.TryGetProperty("description", out var desc)) return desc.GetString();
        return null;
    }

    /// <summary>Set once the stealth script is registered; a navigation then has to wait for it to have run.</summary>
    private bool _stealthInstalled;

    public async Task NavigateAsync(string url, CancellationToken ct = default)
    {
        await SendAsync("Page.navigate", new { url }, ct).ConfigureAwait(false);

        // R193: the surface is registered with addScriptToEvaluateOnNewDocument, so it runs before the page's own
        // scripts — but the probe that follows a navigation was occasionally reading a window it had not reached yet
        // (measured three times: `'chrome' in window` answered true, and a child realm looked unpatched). The marker
        // is the DOCUMENT prunes, not the mask: the mask is installed by step 2 and the prunes by step 15, so an early
        // marker said "ready" while the prune that removes `chrome` had not run yet.
        if (!_stealthInstalled) return;

        for (var i = 0; i < 120; i++)
        {
            var state = await EvaluateAsync("document.readyState + '|' + (typeof window.__documentPrune !== 'undefined')",
                ct).ConfigureAwait(false);
            if (state is not null && state.StartsWith("complete|true", System.StringComparison.Ordinal)) return;
            await Task.Delay(25, ct).ConfigureAwait(false);
        }
    }

    /// <summary>Every x-kpsdk-* request header the page has emitted so far.</summary>
    public Dictionary<string, string> SniffKasadaHeaders()
    {
        var found = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        foreach (var evt in Events)
        {
            if (!evt.TryGetProperty("method", out var method)) continue;
            if (method.GetString() != "Network.requestWillBeSent") continue;
            if (!evt.TryGetProperty("params", out var p)) continue;
            if (!p.TryGetProperty("request", out var req)) continue;
            if (!req.TryGetProperty("headers", out var headers)) continue;

            foreach (var h in headers.EnumerateObject())
            {
                if (h.Name.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
                    found[h.Name] = h.Value.GetString() ?? string.Empty;
            }
        }

        return found;
    }

    /// <summary>
    /// Every x-kpsdk-* header the page saw on a *response*, keyed by the request URL whose reply carried it.
    /// <para>
    /// WHY THIS EXISTS: the interrogation handshake is only observable from both sides. SniffKasadaHeaders
    /// reads what the page sent; this reads what the server answered, which is where the token, the config
    /// and the two headers the sensor validates actually arrive. Without it there is no way to tell a run
    /// that never asked apart from one that asked and was refused.
    /// </para>
    /// </summary>
    public Dictionary<string, Dictionary<string, string>> SniffKasadaResponses()
    {
        var byUrl = new Dictionary<string, Dictionary<string, string>>(StringComparer.OrdinalIgnoreCase);

        foreach (var evt in Events)
        {
            if (!evt.TryGetProperty("method", out var method)) continue;
            if (method.GetString() != "Network.responseReceived") continue;
            if (!evt.TryGetProperty("params", out var p)) continue;
            if (!p.TryGetProperty("response", out var resp)) continue;
            if (!resp.TryGetProperty("headers", out var headers)) continue;

            var url = resp.TryGetProperty("url", out var u) ? u.GetString() : null;
            if (string.IsNullOrEmpty(url)) continue;

            var found = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var h in headers.EnumerateObject())
            {
                if (h.Name.StartsWith("x-kpsdk-", StringComparison.OrdinalIgnoreCase))
                    found[h.Name] = h.Value.GetString() ?? string.Empty;
            }

            // The status travels with it: 200 and 304 mean different things for /mfc (docs/KASADA/11 5.107).
            if (resp.TryGetProperty("status", out var st)) found["status"] = st.ToString();
            if (resp.TryGetProperty("mimeType", out var mt)) found["mimeType"] = mt.GetString() ?? string.Empty;

            if (found.Count > 0) byUrl[url!] = found;
        }

        return byUrl;
    }

    /// <summary>
    /// Every request the page made, in order, paired with whatever the server answered.
    /// <para>
    /// WHY THIS EXISTS: the interrogation is a sequence, not a set of headers. Knowing that a run produced
    /// a token says nothing about which requests produced it, and the order is the only way to see that the
    /// sensor walked from a config fetch to a token fetch. Pairing is by request id, which CDP keeps stable
    /// across requestWillBeSent and responseReceived.
    /// </para>
    /// </summary>
    public List<ChromiumRoundtrip> SniffRoundtrips()
    {
        var byId = new Dictionary<string, ChromiumRoundtrip>(StringComparer.Ordinal);
        var order = new List<string>();

        foreach (var evt in Events)
        {
            if (!evt.TryGetProperty("method", out var method)) continue;
            if (!evt.TryGetProperty("params", out var p)) continue;

            var name = method.GetString();
            if (name == "Network.requestWillBeSent")
            {
                if (!p.TryGetProperty("requestId", out var idEl)) continue;
                var id = idEl.GetString();
                if (string.IsNullOrEmpty(id)) continue;

                if (!byId.TryGetValue(id!, out var rt))
                {
                    rt = new ChromiumRoundtrip { RequestId = id! };
                    byId[id!] = rt;
                    order.Add(id!);
                }

                if (p.TryGetProperty("request", out var req))
                {
                    rt.Method = req.TryGetProperty("method", out var m) ? m.GetString() ?? "" : "";
                    rt.Url = req.TryGetProperty("url", out var u) ? u.GetString() ?? "" : "";
                    if (req.TryGetProperty("headers", out var hs))
                        foreach (var h in hs.EnumerateObject())
                            rt.RequestHeaders[h.Name] = h.Value.GetString() ?? "";
                    if (req.TryGetProperty("postData", out var pd))
                        rt.RequestBody = pd.GetString() ?? "";
                }
            }
            else if (name == "Network.responseReceived")
            {
                if (!p.TryGetProperty("requestId", out var idEl)) continue;
                var id = idEl.GetString();
                if (string.IsNullOrEmpty(id) || !byId.TryGetValue(id!, out var rt)) continue;
                if (!p.TryGetProperty("response", out var resp)) continue;

                rt.Status = resp.TryGetProperty("status", out var st) ? st.GetInt32() : 0;
                rt.MimeType = resp.TryGetProperty("mimeType", out var mt) ? mt.GetString() ?? "" : "";
                if (resp.TryGetProperty("headers", out var hs))
                    foreach (var h in hs.EnumerateObject())
                        rt.ResponseHeaders[h.Name] = h.Value.GetString() ?? "";
            }
        }

        return order.Where(byId.ContainsKey).Select(id => byId[id]).ToList();
    }

    public async ValueTask DisposeAsync()
    {
        try
        {
            if (_socket.State == WebSocketState.Open)
            {
                await _socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "done",
                    CancellationToken.None).ConfigureAwait(false);
            }
        }
        catch (Exception)
        {
            // best effort
        }

        _socket.Dispose();
        _http.Dispose();
        _gate.Dispose();

        try
        {
            if (!_process.HasExited) _process.Kill(entireProcessTree: true);
        }
        catch (Exception)
        {
            // already gone
        }

        // R219: the profile the bridge created is deleted with it. It was never deleted before, and a day of
        // browser-backed tests left 9072 of them (46.7 GB) in %LOCALAPPDATA%\Temp — one per launch. A caller that
        // passed its own profilePath keeps control of that directory: only the temp one this class minted is removed.
        try
        {
            if (_ownsProfile && Directory.Exists(ProfilePath))
            {
                // Chrome keeps handles for a moment after the kill; a short retry beats leaving the directory behind
                for (var attempt = 0; attempt < 3; attempt++)
                {
                    try
                    {
                        Directory.Delete(ProfilePath, recursive: true);
                        break;
                    }
                    catch (IOException)
                    {
                        Thread.Sleep(150);
                    }
                    catch (UnauthorizedAccessException)
                    {
                        Thread.Sleep(150);
                    }
                }
            }
        }
        catch (Exception)
        {
            // a profile left on disk is a leak, but never a reason to fail the caller's dispose
        }

        _process.Dispose();
    }
}

/// <summary>One request the page made and what came back. Mutable while the trace is assembled.</summary>
public sealed class ChromiumRoundtrip
{
    public required string RequestId { get; init; }
    public string Method { get; set; } = "";
    public string Url { get; set; } = "";
    public string RequestBody { get; set; } = "";
    public int Status { get; set; }
    public string MimeType { get; set; } = "";
    public Dictionary<string, string> RequestHeaders { get; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, string> ResponseHeaders { get; } = new(StringComparer.OrdinalIgnoreCase);

    public override string ToString() =>
        $"{Method} {Url} -> {Status} ({RequestBody.Length}b)";
}
