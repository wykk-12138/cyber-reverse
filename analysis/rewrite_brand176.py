import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    public static string BodyJs(IReadOnlyList<string> names)")
end = t.find('    /// <summary>The error a foreign receiver earns.</summary>')

if start < 0 or end < 0:
    raise SystemExit("body region missing")

body = '''    public static string BodyJs(IReadOnlyList<string> names)
    {
        var list = string.Join(", ", names.Select(n => "'" + n + "'"));

        return """
               // ---- brand-checked accessors (R173, corrected in R176) ---------------------------
               // A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that
               // just closes over a constant answers anyone, and that difference needs no reference device to see:
               // pull the descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive
               // override returns the user agent.
               //
               // Two things are easy to get wrong, and the capture says so:
               //
               //   - the message is WEBKIT's, not Blink's "Illegal invocation", because WebKit is the engine being
               //     presented: 'The Navigator.platform getter can only be used on instances of Navigator'
               //   - the brand is checked with Object.prototype.toString, NOT instanceof. Child realms are patched by
               //     copying this descriptor into them, so the closure keeps the PARENT's constructor, and instanceof
               //     is realm-scoped — `this instanceof Navigator` is false for a perfectly good navigator inside an
               //     iframe. The toStringTag survives the realm boundary.
               //
               // And the stack: eliding our own frames is measured and safe, but inventing a native frame is a guess.
               // WebKit adds NO JS frame for an IDL brand check at all, so caller-frames-only is the faithful answer.
               try {
                 const P = G.Navigator && G.Navigator.prototype;

                 // Captured ONCE, here: reading Error.captureStackTrace at throw time would call whatever the page
                 // has installed on it, announcing every brand-check throw and handing the probe a live reference to
                 // the installed getter as its second argument.
                 const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
                 let ELIDE = null;

                 if (P) {
                   const install = (target, name, v, enumerable) => {
                     let brand = null;
                     try { brand = Object.prototype.toString.call(target); } catch (e) { brand = null; }
                     const label = (target && target.constructor && target.constructor.name) || '';

                     const getter = Object.getOwnPropertyDescriptor({
                       get x() {
                         if (brand && brand !== '[object Object]'
                             && Object.prototype.toString.call(this) !== brand) {
                           // Armed with an EMPTY head on purpose: our own frames are dropped, and no native frame is
                           // invented for a check that, in WebKit, never had one.
                           ELIDE = [getter, ''];
                           try {
                             throw new TypeError('The ' + label + '.' + name
                               + ' getter can only be used on instances of ' + label);
                           } finally { ELIDE = null; }
                         }
                         return v;
                       },
                     }, 'x').get;

                     try {
                       const M = G.__nativeMask;
                       if (M && M.getter) return M.getter(function () { return v; }, name);
                     } catch (e) {}
                     return getter;
                   };

                   [__NAMES__].forEach((name) => {
                     try {
                       let current;
                       try { current = G.navigator[name]; } catch (e) { current = undefined; }
                       if (current === undefined) return;

                       const getter = install(P, name, current, true);
                       try {
                         const M = G.__nativeMask;
                         if (M && M.asNative) M.asNative(getter, 'get ' + name, 0);
                       } catch (e) {}
                       try { Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true }); }
                       catch (e) {}

                       Object.defineProperty(P, name,
                         { get: getter, configurable: true, enumerable: true });
                     } catch (e) {}
                   });
                 }
               } catch (e) {}
               """.Replace("__NAMES__", list);
    }

'''

t = t[:start] + body + t[end:]

# the message constant follows the image's formula
t = t.replace('''    /// <summary>The error a foreign receiver earns.</summary>
    public const string IllegalInvocation = "Illegal invocation";''',
'''    /// <summary>
    /// The error a foreign receiver earns, in WebKit's wording rather than Blink's: the engine being presented is the
    /// one whose sentence has to be produced.
    /// </summary>
    public static string MessageFor(string label, string name) =>
        "The " + label + "." + name + " getter can only be used on instances of " + label;''', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the accessor is the image's, wording and all")
