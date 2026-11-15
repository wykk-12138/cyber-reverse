import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) a placeholder the surface can be spliced into, called once per realm
old = '''          const apply = (W) => {
            const N = W.navigator;
            if (!N) return;'''

new = '''          __SURFACE_DEF__

          const apply = (W) => {
            const N = W.navigator;
            if (!N) return;

            // The engine surface is part of the realm patch, because a challenge frame reads
            // WebAssembly itself rather than asking its parent (R146/R148).
            __SURFACE_CALL__'''

if old not in t:
    raise SystemExit("apply anchor missing")
t = t.replace(old, new, 1)

# 2) fill the placeholders at launch, gated on the user agent the profile claims
old2 = '''            source = StealthScript
                .Replace("__HC__", fingerprint.HardwareConcurrency.ToString())'''

new2 = '''            // The two surfaces are corrections of a specific mismatch, so they are installed only when
            // the profile claims the engine they describe. A Chromium build claiming Chromium is already
            // telling the truth about WebAssembly, and a desktop profile must not report a phone's screen.
            var surfaceDef = "const applySurface = (W) => {};";
            if (MobileSurface.IsAppleUserAgent(_userAgent) || WebAssemblySurface.ShouldPatch(_userAgent))
            {
                var body = string.Empty;
                if (WebAssemblySurface.ShouldPatch(_userAgent)) body += WebAssemblySurface.BodyJs();
                if (MobileSurface.IsAppleUserAgent(_userAgent)) body += MobileSurface.BodyJs();

                surfaceDef = "const applySurface = (W) => {\\n" + body + "\\n          };";
            }

            source = StealthScript
                .Replace("__SURFACE_DEF__", surfaceDef)
                .Replace("__SURFACE_CALL__", "applySurface(W);")
                .Replace("__HC__", fingerprint.HardwareConcurrency.ToString())'''

if old2 not in t:
    raise SystemExit("launch anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the bridge splices both surfaces, gated on the claimed engine")
