import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        js += "  try {\\n";
        js += "    if (G.navigator) {\\n";
        js += "      const connection = { effectiveType: '4g', rtt: 50, saveData: false, downlink: 10 };\\n";
        js += "      Object.defineProperty(G.navigator, 'connection',\\n";
        js += "        { get: () => connection, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";'''

new = '''        // R169: on the PROTOTYPE, so the whitelist prune can delete it for a phone claim. Installing it on the
        // instance left `connection` visible on an iPhone profile because the prune only walks the prototype — the
        // measurement said so: phone leaves = ["connection","deviceMemory"].
        js += "  try {\\n";
        js += "    const P = G.Navigator && G.Navigator.prototype;\\n";
        js += "    if (P) {\\n";
        js += "      const connection = { effectiveType: '4g', rtt: 50, saveData: false, downlink: 10 };\\n";
        js += "      Object.defineProperty(P, 'connection',\\n";
        js += "        { get: () => connection, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";'''

if old not in t:
    raise SystemExit("connection anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("connection goes on the prototype so the prune can reach it")
