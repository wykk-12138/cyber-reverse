import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

add = '''
    /// <summary>
    /// True when the user agent claims an Apple device, which is the only case where installing the
    /// phone figures is honest (R148).
    ///
    /// <para>
    /// The same rule as <see cref="WebAssemblySurface.ShouldPatch"/>: these numbers describe a 402×874
    /// iPhone, so putting them on a profile that claims a 363×684 desktop window would replace one
    /// incoherence with another. A patch is not a lie to be sprinkled; it is the correction of a specific
    /// mismatch.
    /// </para>
    /// </summary>
    public static bool IsAppleUserAgent(string? userAgent)
    {
        if (string.IsNullOrEmpty(userAgent)) return false;

        if (userAgent.Contains("iPhone", System.StringComparison.OrdinalIgnoreCase)
            || userAgent.Contains("iPad", System.StringComparison.OrdinalIgnoreCase)) return true;

        return userAgent.Contains("Safari", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chrome", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chromium", System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// The statements the bridge installs in each realm, without a wrapper.
    ///
    /// <para>
    /// Geometry is applied only when the realm is the top-level window: inside a frame the frame's own box
    /// is the honest answer, and a frame that was never shown lays out 0×0, which is worse than a
    /// wrong-but-plausible figure. Everything else — the Screen shape, the alias, the removals, the touch
    /// factory, the pinned box — applies in every realm, because a challenge frame reads those itself.
    /// </para>
    /// </summary>
    public static string BodyJs()
    {
        var js = string.Empty;

        js += "  const G = W;\\n";
        js += "  const value = (target, name, v) => {\\n";
        js += "    try { Object.defineProperty(target, name,\\n";
        js += "      { value: v, writable: true, configurable: true, enumerable: true }); } catch (e) {}\\n";
        js += "  };\\n";

        js += "  const isTop = (() => { try { return G === G.top; } catch (e) { return false; } })();\\n";

        // 1. webkitIndexedDB — a WebKit window is expected to carry the alias
        js += "  try { if (!('" + WebKitAliases[0] + "' in G) && G.indexedDB)\\n";
        js += "    value(G, '" + WebKitAliases[0] + "', G.indexedDB); } catch (e) {}\\n";

        // 2. performance.memory is Blink-only and lives on the prototype, where no prune reaches it
        js += "  try { if (G.Performance && G.Performance.prototype)\\n";
        js += "    delete G.Performance.prototype.memory; } catch (e) {}\\n";

        // 3. the touch factory must return an event, never throw
        js += "  try {\\n";
        js += "    if (G.Document && G.Document.prototype && typeof G.TouchEvent === 'function') {\\n";
        js += "      const createEvent = G.Document.prototype.createEvent;\\n";
        js += "      G.Document.prototype.createEvent = function (type) {\\n";
        js += "        try {\\n";
        js += "          if (arguments.length && String(type).toLowerCase() === 'touchevent')\\n";
        js += "            return " + TouchEventFactory + ";\\n";
        js += "        } catch (e) {}\\n";
        js += "        return createEvent.apply(this, arguments);\\n";
        js += "      };\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        // 4. the Screen shape: the device's keys, in the device's order, and nothing Blink added
        js += "  try {\\n";
        js += "    if (G.Screen && G.Screen.prototype) {\\n";
        js += "      const S = G.Screen.prototype;\\n";
        js += "      const shape = { width: " + ScreenWidth + ", height: " + ScreenHeight +
              ", availWidth: " + ScreenWidth + ", availHeight: " + ScreenHeight + ",\\n";
        js += "        availLeft: 0, availTop: 0, colorDepth: 24, pixelDepth: 24 };\\n";
        js += "      Object.keys(shape).forEach((k) => value(S, k, shape[k]));\\n";
        js += "      const ORDER = [" + string.Join(", ",
              ScreenOrder.Select(k => "'" + k + "'")) + "];\\n";
        js += "      const KEEP = new Set(ORDER);\\n";
        js += "      Object.getOwnPropertyNames(S).forEach((k) => {\\n";
        js += "        if (!KEEP.has(k) && k !== 'constructor') { try { delete S[k]; } catch (e) {} }\\n";
        js += "      });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        // 5. geometry, top level only — and the pinned box that keeps the zoom ratio scroll-invariant
        js += "  if (isTop) {\\n";
        js += "    value(G, 'devicePixelRatio', " + DevicePixelRatio + ");\\n";
        js += "    value(G, 'outerWidth', " + ScreenWidth + ");\\n";
        js += "    value(G, 'outerHeight', " + ScreenHeight + ");\\n";
        js += "    value(G, 'innerWidth', " + ScreenWidth + ");\\n";
        js += "    value(G, 'innerHeight', " + ViewportHeight + ");\\n";
        js += "  }\\n";

        // 6. clientWidth/clientHeight on documentElement, in every realm: the ratio must be exactly 1
        js += "  try {\\n";
        js += "    if (G.Element && G.Element.prototype) {\\n";
        js += "      [['clientWidth', " + ScreenWidth + "], ['clientHeight', " + ViewportHeight + "]]\\n";
        js += "        .forEach((pair) => {\\n";
        js += "          const name = pair[0], want = pair[1];\\n";
        js += "          const original = Object.getOwnPropertyDescriptor(G.Element.prototype, name);\\n";
        js += "          if (!original || !original.get) return;\\n";
        js += "          Object.defineProperty(G.Element.prototype, name, {\\n";
        js += "            configurable: true, enumerable: original.enumerable,\\n";
        js += "            set: original.set,\\n";
        js += "            get: function () {\\n";
        js += "              try {\\n";
        js += "                const doc = this.ownerDocument || G.document;\\n";
        js += "                if (doc && this === doc.documentElement) return want;\\n";
        js += "              } catch (e) {}\\n";
        js += "              return original.get.call(this);\\n";
        js += "            },\\n";
        js += "          });\\n";
        js += "        });\\n";
        js += "    }\\n";
        js += "  } catch (e) {}\\n";

        return js;
    }
}'''

# replace the final closing brace of the class with the new members + brace
idx = t.rstrip().rfind("}")
t = t.rstrip()[:idx].rstrip() + "\n" + add + "\n"

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("MobileSurface exposes BodyJs and the gate")
