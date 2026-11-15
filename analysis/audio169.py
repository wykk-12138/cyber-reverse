import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NavPrune.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>The shape rule this round adds.</summary>"

block = '''    /// <summary>
    /// The <c>audioSession</c> shim, verbatim from the image (R169).
    ///
    /// <code>
    /// // iOS exposes navigator.audioSession, which Blink has no equivalent for, so the prune above cannot restore
    /// // it -- it was never there. hCaptcha serialises each navigator member with JSON.stringify, and on the device
    /// // this one comes back as {} exactly like gpu and clipboard do, so a bare object with the right toStringTag
    /// // reproduces what it reads.
    /// const session = {};
    /// Object.defineProperty(session, Symbol.toStringTag, { value: 'AudioSession', configurable: true });
    /// Object.defineProperty(session, 'type', { value: 'auto', enumerable: false, configurable: true });
    /// value(proto, 'audioSession', session);
    /// </code>
    ///
    /// <para>
    /// A shim does not have to simulate the API; it has to reproduce what the reader serialises. hCaptcha calls
    /// <c>JSON.stringify</c> on each member, and an object with a <c>toStringTag</c> and no enumerable data stringifies to
    /// <c>{}</c> — which is what a real iPhone answers for this member, and for <c>gpu</c> and <c>clipboard</c> too.
    /// </para>
    /// </summary>
    public static string AudioSessionBodyJs()
    {
        return """
               // ---- audioSession (R169) --------------------------------------------------------
               // Not a simulation: JSON.stringify on a bare object with the right toStringTag and no enumerable
               // data answers "{}", which is what the device answers for this member.
               try {
                 const proto = G.Navigator && G.Navigator.prototype;
                 if (proto && !('audioSession' in proto)) {
                   const session = {};
                   Object.defineProperty(session, Symbol.toStringTag,
                     { value: 'AudioSession', configurable: true });
                   Object.defineProperty(session, 'type',
                     { value: 'auto', enumerable: false, configurable: true });
                   Object.defineProperty(proto, 'audioSession',
                     { value: session, writable: true, configurable: true, enumerable: true });
                 }
               } catch (e) {}
               """;
    }

    /// <summary>The tag and the default type the shim carries.</summary>
    public const string AudioSessionTag = "AudioSession";

    /// <inheritdoc cref="AudioSessionTag"/>
    public const string AudioSessionType = "auto";

    /// <summary>
    /// <c>navigator.plugins</c> and <c>mimeTypes</c> are left native, and the image says why: Blink's lists are the
    /// spec's five PDF viewers and two PDF mime types, which is exactly what the iPhone reports (R169).
    /// </summary>
    public const string PluginsAreNative =
        "Blink's lists are the spec's five PDF viewers and two PDF mime types — the same five internal-pdf-viewer "
        + "entries and the same two lengths an iPhone reports; an override used to empty both, on the mistaken belief "
        + "that WebKit's lists are empty, so every bot payload carried plugins: []";

    /// <summary>The lengths a device collector reads off the native lists.</summary>
    public const int NativePluginCount = 5;

    /// <inheritdoc cref="NativePluginCount"/>
    public const int NativeMimeTypeCount = 2;

    /// <summary>The shape rule this round adds.</summary>'''

if anchor not in t:
    raise SystemExit("rule anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, block, 1))
print("audioSession shim and the native-plugins note added")
