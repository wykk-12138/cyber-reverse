import io, re

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    /// <summary>The statements the mobile body installs for a phone profile.</summary>")
end = t.find("/// <summary>The agent test the two surfaces share")
if start < 0 or end < 0:
    raise SystemExit("body region not found")

new_body = '''    /// <summary>
    /// The statements the mobile body installs for a phone profile.
    ///
    /// <para>
    /// Written as a raw string, because R157's first attempt assembled it from escaped concatenations and every
    /// <c>\\n</c> landed as a literal backslash-n outside a string — one SyntaxError, and the browser swallowed it
    /// whole, leaving <c>maxTouchPoints</c> at the host's 10.
    /// </para>
    /// </summary>
    public static string BodyJs()
    {
        var handlers = string.Join(", ", TouchHandlers.Select(h => "'" + h + "'"));

        return """
              try {
                if (G.navigator) {
                  Object.defineProperty(G.navigator, 'maxTouchPoints',
                    { value: __TOUCH__, configurable: true, enumerable: true });
                  Object.defineProperty(G.navigator, 'standalone',
                    { value: false, configurable: true, enumerable: true });
                  if (!('webdriver' in G.navigator)) {
                    Object.defineProperty(G.navigator, 'webdriver',
                      { value: false, configurable: true, enumerable: true });
                  }
                }
              } catch (e) {}

              [__HANDLERS__].forEach((name) => {
                try {
                  if (!(name in G)) {
                    Object.defineProperty(G, name,
                      { value: null, writable: true, configurable: true, enumerable: true });
                  }
                } catch (e) {}
              });
              """
            .Replace("__TOUCH__", MaxTouchPoints.ToString())
            .Replace("__HANDLERS__", handlers);
    }
}

'''

t = t[:start] + new_body + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the touch body is a raw string")
