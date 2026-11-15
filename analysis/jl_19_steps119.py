import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public static readonly Flow JohnLewis = new("johnlewis", new[]
    {
        new Step("GetHome", 20), new Step("WebHandOver", 23), new Step("SessionHandover", 24),'''

new = '''    /// <summary>
    /// John Lewis, <b>nineteen</b> steps.
    ///
    /// <para>
    /// R112 read this flow as seventeen because the step literal jumps from ordinal 20 to 23 and the
    /// gap looked like compiler noise. It is not: the class's <b>lambda literal</b>
    /// (<c>&lt;&lt;FindProduct&gt;g__Available|21_3</c>, <c>&lt;AddToCart&gt;b__22_0</c>) names methods 21
    /// and 22, so <c>FindProduct</c> and <c>AddToCart</c> are steps of the same flow. Nineteen.
    /// </para>
    ///
    /// <para>
    /// The lesson is the same one three rounds have taught: a gap in the ordinals is not permission to
    /// skip it. Nike's 45/47 really were <c>MoveNext</c> helpers; these two are not. The difference is
    /// only visible in a second literal.
    /// </para>
    /// </summary>
    public static readonly Flow JohnLewis = new("johnlewis", new[]
    {
        new Step("GetHome", 20), new Step("FindProduct", 21), new Step("AddToCart", 22),
        new Step("WebHandOver", 23), new Step("SessionHandover", 24),'''

if old not in t:
    raise SystemExit("JL flow anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("John Lewis: 17 -> 19 steps (FindProduct 21, AddToCart 22)")
