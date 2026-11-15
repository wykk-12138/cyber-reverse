import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the model gains the VisualViewport fields, verbatim from the image
old = '''    /// <summary>The two element boxes pinned so the page-zoom ratio cannot move on scroll.</summary>'''
new = '''    /// <summary>
    /// The VisualViewport values the image installs, verbatim (R151):
    /// <c>{offsetLeft: 0, offsetTop: 0, pageLeft: 0, pageTop: 0, width: VW, height: VH, scale: 1}</c>.
    ///
    /// <para>
    /// This is the half of the geometry the replica had left alone. The image's comment says the failure it
    /// fixes: "innerWidth/innerHeight and visualViewport were the only geometry left unpatched, so they
    /// reported the real host window while outerWidth/outerHeight reported the device."
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> VisualViewportFields = new[]
    {
        "offsetLeft", "offsetTop", "pageLeft", "pageTop", "width", "height", "scale",
    };

    /// <summary>
    /// <c>orientation</c> is in the shape but <b>not</b> in the image's value object — the native
    /// <c>ScreenOrientation</c> already says portrait for a phone-sized window, so patching it would be a
    /// claim with nothing to correct (R151).
    /// </summary>
    public const string OrientationIsNative = "orientation";

    /// <summary>The two element boxes pinned so the page-zoom ratio cannot move on scroll.</summary>'''

if old not in t:
    raise SystemExit("vv model anchor missing")
t = t.replace(old, new, 1)

# 2) the body installs them, at the top level only
old2 = '''        // 6. clientWidth/clientHeight on documentElement, in every realm: the ratio must be exactly 1'''
new2 = '''        // 6. VisualViewport, top level only — it is the viewport of the window, not of a frame
        js += "  if (isTop) {\\n";
        js += "    try {\\n";
        js += "      const VV = G.VisualViewport && G.VisualViewport.prototype;\\n";
        js += "      if (VV) {\\n";
        js += "        const vv = { offsetLeft: 0, offsetTop: 0, pageLeft: 0, pageTop: 0,\\n";
        js += "          width: " + ScreenWidth + ", height: " + ViewportHeight + ", scale: 1 };\\n";
        js += "        Object.keys(vv).forEach((k) => value(VV, k, vv[k]));\\n";
        js += "      }\\n";
        js += "    } catch (e) {}\\n";
        js += "  }\\n";

        // 7. clientWidth/clientHeight on documentElement, in every realm: the ratio must be exactly 1'''

if old2 not in t:
    raise SystemExit("clientWidth anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("VisualViewport installed, orientation left native")
