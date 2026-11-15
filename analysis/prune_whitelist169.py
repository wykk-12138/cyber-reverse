import io

# 1) NavPrune becomes whitelist-based, as the image's NAV_PRUNE is
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NavPrune.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''    /// <summary>
    /// Delete the members. Deleting is the point: a trap that throws is still a property, and
    /// <c>for in</c> still walks it.
    /// </summary>
    public static string BodyJs()
    {
        var names = string.Join(", ", BlinkOnly.Select(n => "'" + n + "'"));

        return """
               // ---- pruning (R163) --------------------------------------------------------------
               // Deleted, not trapped: browserleaks reads these straight off navigator, and a property that
               // answers "no" is not the same as a property that is not there.
               [__PRUNE__].forEach((name) => {
                 try {
                   if (name in G.navigator) delete G.navigator[name];
                   const proto = Object.getPrototypeOf(G.navigator);
                   if (proto && name in proto) delete proto[name];
                 } catch (e) {}
               });
               """.Replace("__PRUNE__", names);
    }'''

new1 = '''    /// <summary>
    /// The allowlist the image's <c>NAV_PRUNE</c> deletes against: every own name on
    /// <c>Navigator.prototype</c> that is <b>not</b> in it is removed (R169).
    ///
    /// <para>
    /// R163 wrote this as a nine-name blacklist. The capture is a whitelist — <c>NAV_KEYS</c> has fifty-one entries and
    /// the loop is <c>if (!NAV_KEYS.has(key) &amp;&amp; key !== 'constructor') delete proto[key]</c>. The difference
    /// matters: a blacklist has to be extended every time the engine ships a new interface, and a whitelist cannot fall
    /// behind.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> AllowList =>
        MobileNavigator.NavOrder.Append("plugins").Append("mimeTypes").ToList();

    /// <summary>
    /// Delete every own property of the navigator prototype that is not on the allowlist. Deleting is the point: a trap
    /// that throws is still a property, and <c>for in</c> still walks it.
    /// </summary>
    public static string BodyJs()
    {
        var allowed = string.Join(", ", AllowList.Select(n => "'" + n + "'"));

        return """
               // ---- pruning (R163, whitelist since R169) ----------------------------------------
               // Deleted, not trapped: browserleaks reads these straight off navigator, and a property that
               // answers "no" is not the same as a property that is not there. The image prunes against an
               // allowlist, so an interface Blink ships tomorrow is removed without anyone editing this list.
               try {
                 const proto = G.Navigator && G.Navigator.prototype;
                 if (proto) {
                   const keep = new Set([__ALLOWED__]);
                   Object.getOwnPropertyNames(proto).forEach((key) => {
                     if (!keep.has(key) && key !== 'constructor') {
                       try { delete proto[key]; } catch (e) {}
                     }
                   });
                 }
               } catch (e) {}
               """.Replace("__ALLOWED__", allowed);
    }'''

if old1 not in t1:
    raise SystemExit("prune body anchor missing")
t1 = t1.replace(old1, new1, 1)

# and the doc comment on BlinkOnly now says what it is for
t1 = t1.replace(
    "    /// <summary>The Blink-only members an Apple profile must not expose.</summary>",
    "    /// <summary>\n"
    "    /// The Blink-only members an Apple profile must not expose — kept as the <i>reason</i> the allowlist exists,\n"
    "    /// and as the names to check in a test, even though the mechanism is now whitelist-based (R169).\n"
    "    /// </summary>",
    1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)
print("the prune is whitelist-based")
