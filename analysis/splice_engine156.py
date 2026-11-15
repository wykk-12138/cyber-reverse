import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var surfaceDef = "const applySurface = (realm) => {};";
        if (MobileSurface.IsAppleUserAgent(userAgent) || WebAssemblySurface.ShouldPatch(userAgent))
        {
            var body = string.Empty;
            if (WebAssemblySurface.ShouldPatch(userAgent)) body += WebAssemblySurface.BodyJs();
            if (MobileSurface.IsAppleUserAgent(userAgent)) body += MobileSurface.BodyJs();

            surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + body + "\\n          };";
        }'''

new = '''        // The engine block is unconditional: it is what a real Chromium reports (five plugins, the connection
        // quartet, the two flags the image's payload carries), so it is true for every profile. The two
        // gated blocks below it correct a *specific* claim and must not be installed otherwise (R148/R156).
        var surfaceBody = MobileSurface.EngineBodyJs();

        if (MobileSurface.IsAppleUserAgent(userAgent) || WebAssemblySurface.ShouldPatch(userAgent))
        {
            if (WebAssemblySurface.ShouldPatch(userAgent)) surfaceBody += WebAssemblySurface.BodyJs();
            if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += MobileSurface.BodyJs();
        }

        var surfaceDef = "const applySurface = (realm) => {\\n  const G = realm;\\n" + surfaceBody +
                         "\\n          };";'''

if old not in t:
    raise SystemExit("surface def anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the engine block is installed for every profile")
