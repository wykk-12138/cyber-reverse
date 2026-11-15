import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    public static string BodyJs(string? userAgent)")
end = t.find('/// <summary>The agent test the two surfaces share')
if start < 0 or end < 0:
    raise SystemExit("body region not found")

body = '''    public static string BodyJs(string? userAgent)
    {
        var handlers = string.Join(", ", TouchHandlers.Select(h => "'" + h + "'"));
        var language = Captured["language"];

        var js = """
                 try {
                   const N = G.navigator;
                   if (N) {
                     // R164: the image installs these on Navigator.prototype, not on the instance. A detector can
                     // read either, but `Object.getOwnPropertyNames(navigator)` answers differently, and the
                     // capture is written as `Object.keys(NAV).forEach((key) => value(Navigator.prototype, key, …))`.
                     const P = Object.getPrototypeOf(N);
                     const put = (name, v) => {
                       try {
                         const target = (P && name in P) ? P : N;
                         if (target[name] === v) return;
                         Object.defineProperty(target, name,
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
                     put('language', '__LANGUAGE__');

                     if (!('webdriver' in N)) put('webdriver', false);

                     // appVersion is the agent minus Mozilla/ — one value, two properties
                     const ua = N.userAgent || '';
                     if (ua) put('appVersion', ua.indexOf('Mozilla/') === 0 ? ua.slice(8) : ua);

                     // R164: languages is ONE element, frozen. The image writes
                     //   value(Navigator.prototype, 'languages', Object.freeze([NAV.language]))
                     // — a phone with a single language, not the usual two-element list.
                     try {
                       Object.defineProperty(P && 'languages' in P ? P : N, 'languages',
                         { value: Object.freeze(['__LANGUAGE__']), writable: false,
                           configurable: true, enumerable: true });
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
            .Replace("__LANGUAGE__", language)
            .Replace("__HANDLERS__", handlers);

        return js;
    }
}

'''

t = t[:start] + body + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("values go on the prototype, languages is one element")
