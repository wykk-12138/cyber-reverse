import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

broken = '''        await SendAsync("Page.addScriptToEvaluateOnNewDocument", new
        {
            // The two surfaces are corrections of a specific mismatch, so they are installed only when
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
                .Replace("__HC__", fingerprint.HardwareConcurrency.ToString())
                .Replace("__DM__", fingerprint.DeviceMemory.ToString()),
        }, ct).ConfigureAwait(false);'''

fixed = '''        // The two surfaces are corrections of a specific mismatch, so they are installed only when the
        // profile claims the engine they describe. A Chromium build claiming Chromium already tells the
        // truth about WebAssembly, and a desktop profile must not report a phone's screen (R148).
        var surfaceDef = "const applySurface = (W) => {};";
        if (MobileSurface.IsAppleUserAgent(_userAgent) || WebAssemblySurface.ShouldPatch(_userAgent))
        {
            var body = string.Empty;
            if (WebAssemblySurface.ShouldPatch(_userAgent)) body += WebAssemblySurface.BodyJs();
            if (MobileSurface.IsAppleUserAgent(_userAgent)) body += MobileSurface.BodyJs();

            surfaceDef = "const applySurface = (W) => {\\n" + body + "\\n          };";
        }

        var source = StealthScript
            .Replace("__SURFACE_DEF__", surfaceDef)
            .Replace("__SURFACE_CALL__", "applySurface(W);")
            .Replace("__HC__", fingerprint.HardwareConcurrency.ToString())
            .Replace("__DM__", fingerprint.DeviceMemory.ToString());

        await SendAsync("Page.addScriptToEvaluateOnNewDocument", new
        {
            source,
        }, ct).ConfigureAwait(false);'''

if broken not in t:
    raise SystemExit("broken region anchor mismatch")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(broken, fixed, 1))
print("the splice sits above the addScript call, not inside its initialiser")
