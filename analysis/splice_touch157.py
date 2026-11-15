import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            if (MobileSurface.IsAppleUserAgent(userAgent)) surfaceBody += MobileSurface.BodyJs();'''

new = '''            if (MobileSurface.IsAppleUserAgent(userAgent))
            {
                surfaceBody += MobileSurface.BodyJs();

                // R157: the touch surface. `'ontouchstart' in window` is not decoration — the image's own note
                // records a wall gating its worker path on it, paired with the user agent's shape.
                surfaceBody += MobileNavigator.BodyJs();
            }'''

if old not in t:
    raise SystemExit("mobile gate anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the touch surface installs with the phone surface")
