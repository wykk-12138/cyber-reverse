import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        js += "  if (isTop) {\\n";
        js += "    value(G, 'devicePixelRatio', " + DevicePixelRatio + ");\\n";
        js += "    value(G, 'outerWidth', " + ScreenWidth + ");\\n";
        js += "    value(G, 'outerHeight', " + ScreenHeight + ");\\n";
        js += "    value(G, 'innerWidth', " + ScreenWidth + ");\\n";
        js += "    value(G, 'innerHeight', " + ViewportHeight + ");\\n";
        js += "  }\\n";'''

new = '''        // R150: these four are pinned with getters rather than assigned. An assigned value is a plain
        // data property, and the browser re-derives outerHeight when the window is resized — which the
        // host does after the script runs. A getter survives that, and it is also what "the profile says
        // this is the device" means: the page cannot observe anything else.
        js += "  if (isTop) {\\n";
        js += "    const pin = (name, v) => {\\n";
        js += "      try { Object.defineProperty(G, name, { configurable: true, get: () => v }); } catch (e) {}\\n";
        js += "    };\\n";
        js += "    pin('devicePixelRatio', " + DevicePixelRatio + ");\\n";
        js += "    pin('outerWidth', " + ScreenWidth + ");\\n";
        js += "    pin('outerHeight', " + ScreenHeight + ");\\n";
        js += "    pin('innerWidth', " + ScreenWidth + ");\\n";
        js += "    pin('innerHeight', " + ViewportHeight + ");\\n";
        js += "  }\\n";'''

if old not in t:
    raise SystemExit("geometry block anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("geometry is pinned with getters, which a resize cannot overwrite")
