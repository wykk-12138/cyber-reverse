"""R1338b: the edit pass silently ate the CRLFs inside a verbatim string.

The decoded addLineItem document contains CRLF — 206 of them — and the embedded constant came out 206
characters short after I used the `edit` tool to fix an unrelated identifier. The tool normalises line endings
when it rewrites a file, and a verbatim C# string (`@"..."`) carries real newlines, so the document lost its
line endings without any test noticing until the length check fired.

That is the same class of bug as R1326's hand-pasted document, one level down: not the characters, but the
invisible ones. The repair is to stop storing the document as raw text at all — it becomes a regular string
literal with explicit \\r\\n escapes, which no line-ending normalisation can touch, and a test asserts the exact
CRLF count so a future pass is caught immediately rather than by a length that happens to differ.

Usage: python analysis/fix_document_line_endings.py
"""
import io
import json

DOCS = 'analysis/.highsnobiety_docs.json'
PATHS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
TESTS = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'

documents = json.loads(io.open(DOCS, encoding='utf-8').read())


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


source = io.open(PATHS, encoding='utf-8', newline='').read()

for name, constant in (('add_line_item', 'AddLineItemDocument'), ('add_discount_code', 'AddDiscountCodeDocument')):
    document = documents[name]
    start = source.find('    public const string %s = @"' % constant)
    if start < 0:
        raise SystemExit('%s declaration not found' % constant)
    end = source.find('";\n', start)
    if end < 0:
        raise SystemExit('%s terminator not found' % constant)
    replacement = '    public const string %s =\n        "%s' % (constant, escape_literal(document))
    source = source[:start] + replacement + source[end:]
    print('%s: %d chars, %d CRLF' % (constant, len(document), document.count('\r\n')))

io.open(PATHS, 'w', encoding='utf-8', newline='').write(source)
print('rewrote both constants as escaped literals')

tests = io.open(TESTS, encoding='utf-8', newline='').read()
if 'TheDocumentKeepsItsLineEndings' in tests:
    raise SystemExit('guard already present')

guard = '''
    /// <summary>
    /// R1338: the document carries CRLF, and a text-editor pass over this file silently turned them into LF —
    /// 206 characters vanished from a verbatim string with nothing to catch it. The literal now spells \\r\\n
    /// out, and this pins the count so the next pass fails loudly instead of quietly.
    /// </summary>
    [Fact]
    public void TheDocumentKeepsItsLineEndings()
    {
        Assert.Equal(206, CountOf(HighsnobietyFlow.AddLineItemDocument, "\\r\\n"));
        Assert.DoesNotContain("\\n", HighsnobietyFlow.AddLineItemDocument.Replace("\\r\\n", ""));
        Assert.Equal(206, CountOf(HighsnobietyFlow.AddDiscountCodeDocument, "\\r\\n"));
    }

    private static int CountOf(string text, string needle)
    {
        var count = 0;
        var index = text.IndexOf(needle, System.StringComparison.Ordinal);
        while (index >= 0)
        {
            count++;
            index = text.IndexOf(needle, index + needle.Length, System.StringComparison.Ordinal);
        }

        return count;
    }
}
'''

tests = tests.rstrip()
tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + guard
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('added the line-ending guard')
