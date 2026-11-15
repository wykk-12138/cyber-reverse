import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\WebAssemblySurface.cs"
t = io.open(p, encoding="utf-8").read()

# The arithmetic in CountsDifferByTheDelta was backwards: Blink has three extra names and two fewer
# methods, so the counts differ by 3 - 2 in the opposite direction.
old = '''    /// <summary>True when the two count vectors differ exactly by <see cref="Delta"/>.</summary>
    public static bool CountsDifferByTheDelta =>
        BlinkCounts[0] - SafariCounts[0] == JspiNames.Count - TypeReflectionMethods.Count;'''

new = '''    /// <summary>
    /// True when the first count moves by exactly the names removed.
    ///
    /// <para>
    /// Blink answers 19 and Safari 16, and the three JSPI names are what Blink has extra. The two added
    /// methods land on <c>Memory.prototype</c> and <c>Table.prototype</c>, whose counts go 5 → 6, so the
    /// first vector is untouched by them. The arithmetic has to respect that direction, which is what
    /// R146's first attempt got wrong.
    /// </para>
    /// </summary>
    public static bool CountsDifferByTheDelta =>
        BlinkCounts[0] - SafariCounts[0] == JspiNames.Count
        && SafariCounts[3] - BlinkCounts[3] == 1
        && SafariCounts[4] - BlinkCounts[4] == 1;'''

if old not in t:
    raise SystemExit("delta anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the delta arithmetic points the right way")
