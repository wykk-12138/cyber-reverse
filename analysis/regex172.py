import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the constants, verbatim from the image
old = '''    /// <summary>The text a native function answers with, per name.</summary>
    public static string NativeText(string name) => "function " + name + "() { [native code] }";'''

new = '''    /// <summary>
    /// The shape V8 prints for a native: one line, <c>{ [native code] }</c>. Captured from the image (R172) as
    /// <c>/^(function [^(]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/</c>.
    /// </summary>
    public const string V8Native = @"^(function [^(]*\(\)|class [^ ]*) \{ \[native code\] \}$";

    /// <summary>
    /// V8 writes an accessor's role into its source — <c>function get navigation() { … }</c> — and the device does not.
    /// Captured as <c>/^function (?:get|set) (?=[^\\s(])/</c>; the lookahead is what leaves a function genuinely named
    /// <c>get</c> (<c>Map.prototype.get</c>) alone.
    /// </summary>
    public const string V8Accessor = @"^function (?:get|set) (?=[^\s(])";

    /// <summary>
    /// The text WebKit answers with: the same name, then a newline and four spaces. R172's finding is that the cloak
    /// <b>reformats</b> V8's one-line form into this one, because the profile claims a WebKit engine.
    /// </summary>
    public static string WebKitText(string name) => "function " + name + "() {\\n    [native code]\\n}";

    /// <summary>The text a native function answers with, per name, in the engine the profile claims.</summary>
    public static string NativeText(string name) => WebKitText(name);'''

if old not in t:
    raise SystemExit("native text anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the two regexes and the WebKit text are recorded")
