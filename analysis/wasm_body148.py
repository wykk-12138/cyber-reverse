import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\WebAssemblySurface.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>
    /// The JavaScript that turns Blink's surface into Safari's, in the shape the image uses: delete the
    /// three JSPI names, add two non-enumerable methods whose bodies answer rather than throw.
    /// </summary>
    public static string ToJavaScript()
    {
        var js = string.Empty;'''

new = '''    /// <summary>
    /// True when the supplied user agent claims a WebKit engine, which is the only case where this patch
    /// is honest: the counts below are Blink's real numbers, so a profile that claims Chromium needs
    /// nothing done to it (R148).
    /// </summary>
    public static bool ShouldPatch(string? userAgent)
    {
        if (string.IsNullOrEmpty(userAgent)) return false;

        // iPhone/iPad, and desktop Safari which also reports Version/… Safari/…
        if (userAgent.Contains("iPhone", System.StringComparison.OrdinalIgnoreCase)
            || userAgent.Contains("iPad", System.StringComparison.OrdinalIgnoreCase)) return true;

        return userAgent.Contains("Safari", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chrome", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chromium", System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// The statements, without a wrapper — for a caller that needs to place them inside a larger function
    /// such as the bridge's per-realm <c>apply</c>.
    /// </summary>
    public static string BodyJs()
    {
        var js = string.Empty;
        js += "  if (!G.WebAssembly) return;\\n";
        js += "  const W = G.WebAssembly;\\n";
        js += "  [" + string.Join(", ", JspiNames.Select(n => "\\"" + n + "\\"")) + "]\\n";
        js += "    .forEach((name) => { try { delete W[name]; } catch (e) {} });\\n";
        js += "  const addMethod = (target, name, impl) => {\\n";
        js += "    if (!target || name in target) return;\\n";
        js += "    const fn = function () { return impl.apply(this, arguments); };\\n";
        js += "    Object.defineProperty(fn, 'name', { value: name, configurable: true });\\n";
        js += "    Object.defineProperty(fn, 'length', { value: 0, configurable: true });\\n";
        js += "    Object.defineProperty(target, name,\\n";
        js += "      { value: fn, writable: true, configurable: true, enumerable: false });\\n";
        js += "  };\\n";
        js += "  if (W.Memory) addMethod(W.Memory.prototype, 'type', function () { return { kind: 'memory' }; });\\n";
        js += "  if (W.Table) addMethod(W.Table.prototype, 'type', function () { return { kind: 'table' }; });\\n";
        return js;
    }

    /// <summary>
    /// The JavaScript that turns Blink's surface into Safari's, in the shape the image uses: delete the
    /// three JSPI names, add two non-enumerable methods whose bodies answer rather than throw.
    /// </summary>
    public static string ToJavaScript()
    {
        var js = string.Empty;'''

if old not in t:
    raise SystemExit("ToJavaScript anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("WebAssemblySurface exposes BodyJs and the gate")
