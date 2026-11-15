import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\BrowserFingerprint.cs"
t = io.open(p, encoding="utf-8").read()

start = t.index("        return $\"\"\"")
end = t.index("            \"\"\";", start) + len("            \"\"\";")

replacement = '''        // A raw interpolated string with doubled braces is unreadable here; plain concatenation keeps
        // the JavaScript visible and avoids the CS9006 brace-count rule entirely.
        var js = string.Empty;
        js += "(function () {\\n";
        js += "  try {\\n";
        js += "    const N = Navigator.prototype;\\n";
        js += "    Object.defineProperty(N, 'hardwareConcurrency', { get: () => " + HardwareConcurrency + ", configurable: true });\\n";
        js += "    Object.defineProperty(N, 'deviceMemory', { get: () => " + DeviceMemory + ", configurable: true });\\n";
        js += "    Object.defineProperty(N, 'maxTouchPoints', { get: () => 0, configurable: true });\\n";
        js += "    Object.defineProperty(window, 'devicePixelRatio', { get: () => " + ratio + ", configurable: true });\\n";
        js += "    const S = Screen.prototype;\\n";
        js += "    Object.defineProperty(S, 'width', { get: () => " + ScreenWidth + ", configurable: true });\\n";
        js += "    Object.defineProperty(S, 'height', { get: () => " + ScreenHeight + ", configurable: true });\\n";
        js += "    Object.defineProperty(S, 'availWidth', { get: () => " + AvailableScreenWidth + ", configurable: true });\\n";
        js += "    Object.defineProperty(S, 'availHeight', { get: () => " + AvailableScreenHeight + ", configurable: true });\\n";
        js += "    Object.defineProperty(S, 'colorDepth', { get: () => " + ColorDepth + ", configurable: true });\\n";
        js += "    Object.defineProperty(S, 'pixelDepth', { get: () => " + ColorDepth + ", configurable: true });\\n";
        js += "  } catch (e) {}\\n";
        js += "})();\\n";
        return js;'''

t = t[:start] + replacement + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ToJavaScript rewritten without raw-string braces")
