import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    /// <summary>Why a data property is not enough.</summary>'''

block = '''    /// <summary>
    /// The image's <c>value()</c> tail, recorded because it is the part that has to be copied exactly (R177):
    /// </summary>
    /// <code>
    /// Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true });
    /// Object.defineProperty(target, name, {
    ///   get: getter,
    ///   configurable: true,
    ///   enumerable: enumerable !== false,
    /// });
    /// record(target, name);
    /// </code>
    public const string ValueTail =
        "get: getter, configurable: true, enumerable: enumerable !== false — then record(target, name)";

    /// <summary>
    /// The image's <c>method()</c>: a replacement whose <c>length</c> comes from the ORIGINAL, whose name is the same,
    /// and which keeps the original as its first argument.
    /// </summary>
    public const string MethodShape =
        "the arity of a patched method comes from the ORIGINAL, and the original is handed to the builder as its "
        + "first argument";

    /// <summary>
    /// The image's <c>reseat</c>, which this workspace implements as <see cref="NavOrder.ReseatBodyJs"/> — recorded here
    /// because R177 measured that the two agree: descriptors carried across untouched, non-configurable members left
    /// alone, and anything the device did not list keeping its relative order at the end.
    /// </summary>
    public const string ReseatShape =
        "delete then define appends: kept descriptors are carried across untouched, unlisted members keep their "
        + "relative order at the end, and non-configurable members are left alone";

    /// <summary>Why a data property is not enough.</summary>'''

if anchor not in t:
    raise SystemExit("rule doc anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, block, 1))
print("three shapes recorded")
