import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs"
t = io.open(p, encoding='utf-8').read()
old = '''public sealed class SmartActionUtilitiesDocument
{
    public List<string> Utilities { get; set; } = new();
}'''
new = '''public sealed class SmartActionUtilitiesDocument
{
    /// <summary>
    /// The saved utility groups (the store lists the Utilities page edits). The key is <c>groups</c>: a live
    /// <c>smartActionUtilities.json</c> contains exactly <c>{"groups": …}</c> (R386), so the property is named after it rather
    /// than after the file.
    /// </summary>
    public List<string> Groups { get; set; } = new();
}'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('Utilities -> Groups (live key is "groups")')
