import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

add = '''
    /// <summary>
    /// The engine-level members R156 added: five plugins, the connection quartet, and the image's two
    /// non-standard flags.
    ///
    /// <para>
    /// These are <b>not</b> mobile figures — they are what a real Chromium reports — so this body is installed
    /// for every profile, not gated. The plugin list is five because the sample says
    /// <c>navigator.plugins.count = 5</c> and all five share <c>internal-pdf-viewer</c>; the replica had three,
    /// which a count alone would catch.
    /// </para>
    /// </summary>
    public static string EngineBodyJs()
    {
        var js = string.Empty;

        // 1. five plugins, and a length that matches the list rather than a fixed number
        js += "  try {\\n";
        js += "    const names = [" + string.Join(", ",
              SessionPayload.PluginNames.Select(n => "'" + n + "'")) + "];\\n";
        js += "    const plugins = names.map((name) => Object.freeze({ name: name,\\n";
        js += "      filename: '" + SessionPayload.PluginFilename + "',\\n";
        js += "      description: '" + SessionPayload.PluginDescription + "' }));\\n";
        js += "    Object.freeze(plugins);\\n";
        js += "    if (G.navigator) {\\n";
        js += "      Object.defineProperty(G.navigator, 'plugins',\\n";
        js += "        { get: () => plugins, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        // 2. the connection quartet, with the sample's values
        js += "  try {\\n";
        js += "    if (G.navigator) {\\n";
        js += "      const connection = { effectiveType: '4g', rtt: 50, saveData: false, downlink: 10 };\\n";
        js += "      Object.defineProperty(G.navigator, 'connection',\\n";
        js += "        { get: () => connection, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        // 3. the two flags the image reports beside the readings they came from
        js += "  try {\\n";
        js += "    if (G.navigator && !('automationEnabled' in G.navigator)) {\\n";
        js += "      Object.defineProperty(G.navigator, 'automationEnabled',\\n";
        js += "        { value: false, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        js += "  try {\\n";
        js += "    if (G.Screen && G.Screen.prototype) {\\n";
        js += "      const darkMode = Object.freeze({ enabled: " +
              (SessionPayload.DarkModeSample ? "true" : "false") + " });\\n";
        js += "      Object.defineProperty(G.Screen.prototype, 'darkMode',\\n";
        js += "        { get: () => darkMode, configurable: true, enumerable: true });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        return js;
    }
}'''

idx = t.rstrip().rfind("}")
t = t.rstrip()[:idx].rstrip() + "\n" + add + "\n"

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("engine body added")
