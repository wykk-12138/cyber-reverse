import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()

old = '''            .Select(File.ReadAllText));'''
new = '''            .Select(f => StripComments(File.ReadAllText(f))));'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    private static string Root()'''
add = '''    /// <summary>
    /// Removes comments before matching. Without this a name like <c>Plus</c> looks "present" because some unrelated
    /// comment says "plus" — R249 found exactly that: the ledger had been counting prose as code.
    /// </summary>
    private static string StripComments(string text)
    {
        text = Regex.Replace(text, @"/\\*.*?\\*/", " ", RegexOptions.Singleline);
        return Regex.Replace(text, @"//[^\\n]*", " ");
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('matcher now ignores comments')
