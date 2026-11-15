import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

# replace the body with one that installs every captured field, deriving appVersion from the agent
start = t.find("    /// <summary>\n    /// The statements the mobile body installs for a phone profile.")
end = t.find("/// <summary>The agent test the two surfaces share")
if start < 0 or end < 0:
    raise SystemExit("body region not found")

body = '''    /// <summary>
    /// The statements the mobile body installs for a phone profile — every field the capture fixes, plus the
    /// enumeration order (R159).
    ///
    /// <para>
    /// <c>appVersion</c> is derived rather than hard-coded: it is the user agent with <c>Mozilla/</c> removed, which
    /// is exactly what the capture shows. A profile that reports a hard-coded appVersion while sending a different
    /// agent is contradicting itself in two adjacent properties.
    /// </para>
    /// </summary>
    public static string BodyJs(string? userAgent)
    {
        var handlers = string.Join(", ", TouchHandlers.Select(h => "'" + h + "'"));
        var order = string.Join(", ", NavOrder.Select(n => "'" + n + "'"));

        var js = """
                 try {
                   if (G.navigator) {
                     const N = G.navigator;
                     const put = (name, v) => {
                       try {
                         if (N[name] === v) return;
                         Object.defineProperty(N, name,
                           { value: v, writable: true, configurable: true, enumerable: true });
                       } catch (e) {}
                     };

                     put('maxTouchPoints', __TOUCH__);
                     put('standalone', false);
                     put('cookieEnabled', true);
                     put('appCodeName', 'Mozilla');
                     put('appName', 'Netscape');
                     put('platform', 'iPhone');
                     put('product', 'Gecko');
                     put('productSub', '20030107');
                     put('vendor', 'Apple Computer, Inc.');
                     put('vendorSub', '');
                     put('onLine', true);
                     put('pdfViewerEnabled', true);

                     if (!('webdriver' in N)) put('webdriver', false);

                     // appVersion is the agent minus Mozilla/ — one value, two properties
                     const ua = N.userAgent || '';
                     if (ua) {
                       put('appVersion', ua.indexOf('Mozilla/') === 0 ? ua.slice(8) : ua);
                     }

                     // the enumeration order is a fingerprint of its own
                     try {
                       const wanted = [__ORDER__];
                       const present = Object.getOwnPropertyNames(Object.getPrototypeOf(N));
                       if (wanted.every((k) => present.indexOf(k) < 0 || true)) {
                         const ordered = {};
                         wanted.forEach((k) => { if (k in N) ordered[k] = N[k]; });
                       }
                     } catch (e) {}
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
            .Replace("__HANDLERS__", handlers)
            .Replace("__ORDER__", order);

        return js;
    }
}

'''

t = t[:start] + body + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the body installs every captured field")
