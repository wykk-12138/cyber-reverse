"""Add a guard so a pasted truncation marker can never ship again, and pin the repaired document."""

import io

TEST = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(TEST, encoding='utf-8').read()

if 'NoDocumentCarriesATruncationMarker' in text:
    raise SystemExit('guard already present')

block = '''
    /// <summary>
    /// R1326: the onboarding document shipped for months ending with "[4040 chars total]" — a truncation
    /// marker pasted out of a display, which left the document stopping mid-way. The image's copy is 4040
    /// characters; this pins the repaired text and the absence of the marker in every generated document, so
    /// the same paste cannot ship again.
    /// </summary>
    [Fact]
    public void TheOnboardDocumentIsWholeAndCarriesNoTruncationMarker()
    {
        var document = WarhammerQueries.ApproveOnboardPaymentMutation;

        Assert.Equal(4040, document.Length);
        Assert.DoesNotContain("chars total", document);
        Assert.EndsWith("__typename\\n}", document.TrimEnd() + "\\n}");
        Assert.Contains("approveGuestSignUpPayment", document);

        foreach (var field in typeof(WarhammerQueries).GetFields(
                     System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
        {
            var value = field.GetValue(null) as string;
            if (value is null) continue;
            Assert.DoesNotContain("chars total", value);
        }
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TEST, 'w', encoding='utf-8', newline='').write(text)
print('appended the truncation guard')
