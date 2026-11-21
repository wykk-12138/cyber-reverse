"""Replace the string-surgery assertion with a declared-set comparison, which is what the claim actually is."""

import io
import re

TESTS = 'replica/tests/Cybersole.Tests/PayPalPartnerApproveTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

start = text.find("    /// <summary>The difference between the two documents is that one name, and nothing else.</summary>")
end = text.find("    /// <summary>The envelope picks the document from the variables it is given.</summary>")
if start < 0 or end < 0:
    raise SystemExit('block not found')

replacement = '''    /// <summary>
    /// The difference between the two documents is that one declared name, and nothing else. Comparing the declared
    /// sets says that directly; running string surgery on 3000 characters of GraphQL does not.
    /// </summary>
    [Fact]
    public void TheTwoDocumentsDifferByThatOneName()
    {
        static System.Collections.Generic.HashSet<string> Declared(string document) =>
            new(System.Text.RegularExpressions.Regex.Matches(document, @"\\$(\\w+)\\s*:")
                .Select(m => m.Groups[1].Value));

        var shortSet = Declared(PayPalPartnerApprove.Document);
        var longSet = Declared(PayPalPartnerApprove.PaycodeDocument);

        var onlyInLong = new System.Collections.Generic.HashSet<string>(longSet);
        onlyInLong.ExceptWith(shortSet);
        var onlyInShort = new System.Collections.Generic.HashSet<string>(shortSet);
        onlyInShort.ExceptWith(longSet);

        Assert.Equal(new[] { "paycodeEncrypted" }, System.Linq.Enumerable.OrderBy(onlyInLong, name => name));
        Assert.Empty(onlyInShort);
        Assert.Equal(15, shortSet.Count);
        Assert.Equal(16, longSet.Count);
    }

'''

text = text[:start] + replacement + text[end:]
if 'using System.Linq;' not in text:
    text = 'using System.Linq;\n' + text
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('replaced with a declared-set comparison')
