"""The document declares four variables; the sender fills two. Say both."""

import io

PATH = 'replica/src/Cybersole.Stores/Flows/StorefrontApiProduct.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

old = '''    /// <summary>The two variable keys the sender fills.</summary>
    public static readonly string[] VariableNames = { "id", "variationId" };'''

new = '''    /// <summary>
    /// The four variables the document declares — <c>$id</c>, <c>$isDraft</c>, <c>$variationId</c>, <c>$src</c>.
    /// </summary>
    public static readonly string[] DeclaredVariables = { "id", "isDraft", "variationId", "src" };

    /// <summary>
    /// The two the sender actually fills. The other two are optional in the document and this class does not
    /// invent values for them: a draft product and a source override change what the query returns.
    /// </summary>
    public static readonly string[] SenderVariables = { "id", "variationId" };'''

if text.count(old) != 1:
    raise SystemExit('variable block not found')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('split declared from sender variables')
