import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        js += "    pin('devicePixelRatio', " + DevicePixelRatio + ");\\n";
        js += "    pin('outerWidth', " + ScreenWidth + ");\\n";
        js += "    pin('outerHeight', " + ScreenHeight + ");\\n";
        js += "    pin('innerWidth', " + ScreenWidth + ");\\n";
        js += "    pin('innerHeight', " + ViewportHeight + ");\\n";
        js += "  }\\n";'''

new = '''        js += "    const pinAll = () => {\\n";
        js += "      pin('devicePixelRatio', " + DevicePixelRatio + ");\\n";
        js += "      pin('outerWidth', " + ScreenWidth + ");\\n";
        js += "      pin('outerHeight', " + ScreenHeight + ");\\n";
        js += "      pin('innerWidth', " + ScreenWidth + ");\\n";
        js += "      pin('innerHeight', " + ViewportHeight + ");\\n";
        js += "    };\\n";
        js += "    pinAll();\\n";
        // Chromium installs its own window geometry once the window is realised, which is after
        // document-start — R150 measured exactly that: the accessor was accepted, and 769 was back a
        // moment later. Re-pinning at the three moments the browser settles geometry is what makes the
        // claim stick; the descriptor is configurable, so each re-pin replaces its accessor.
        js += "    ['DOMContentLoaded', 'load', 'resize'].forEach((ev) => {\\n";
        js += "      try { G.addEventListener(ev, pinAll); } catch (e) {}\\n";
        js += "    });\\n";
        js += "  }\\n";'''

if old not in t:
    raise SystemExit("pin block anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("geometry re-pins at DOMContentLoaded, load and resize")
