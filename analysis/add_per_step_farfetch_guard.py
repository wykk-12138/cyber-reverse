"""R1295 (cont.): make the Farfetch guard per-step, because a file-wide assertion proves nothing per step.

The mutation that empties one message left the tests green: six other messages still carried every phrase the assertion
looked for, so the guard was measuring the file, not the step. This adds a per-step check — the message for each of the
seven routes must itself carry the classification, the server-delivered note, the connect/app config and the credential.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tests/Cybersole.Tests/FarfetchIsCoveredByTheOriginalTests.cs'
text = io.open(P, encoding='utf-8').read()

marker = '    [Fact]\n    public void TheStepsNameTheServerDeliveredTransport()'
idx = text.find(marker)
if idx < 0:
    raise SystemExit('anchor test not found')

new_test = '''    /// <summary>
    /// R1295: the classification has to be on <em>each</em> message, not somewhere in the file.
    ///
    /// <para>
    /// The file-wide assertion below passed even after one message was emptied, because the other six still mention
    /// server-delivered and the credential. This one reads the line that names the step and requires the four phrases
    /// there, which is what a regression would actually remove.
    /// </para>
    /// </summary>
    [Theory]
    [InlineData("product")]
    [InlineData("add-to-cart")]
    [InlineData("basket")]
    [InlineData("checkout")]
    [InlineData("shipping")]
    [InlineData("payment")]
    [InlineData("place-order")]
    public void EachStepCarriesTheReasonItself(string step)
    {
        var line = Source()
            .Split('\\n')
            .FirstOrDefault(l => l.Contains("farfetch: " + step + " ", StringComparison.Ordinal));

        Assert.NotNull(line);
        Assert.Contains("route unrecorded locally", line, StringComparison.Ordinal);
        Assert.Contains("server-delivered", line, StringComparison.Ordinal);
        Assert.Contains("connect/app", line, StringComparison.Ordinal);
        Assert.Contains("schema needs the original login", line, StringComparison.Ordinal);
    }

'''

text = text[:idx] + new_test + text[idx:]
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('per-step test inserted before the file-wide one')
