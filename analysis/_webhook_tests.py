import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\WebhookCreatorLabelTests.cs"
code = '''using Cybersole.Ui.Views.Settings.Modals;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R340: the New Webhook form's submit button, measured on the running 5.18.32 build.
///
/// <para>
/// The button is a three-state machine and its text is the message: with an empty name it reads "Enter name"; with a
/// name but an unparseable URL it reads "Enter valid webhook"; with both good it reads "Save" and is the only enabled
/// state. All three were read off the live modal in this round, in that order.
/// </para>
/// </summary>
public sealed class WebhookCreatorLabelTests
{
    private readonly ITestOutputHelper _out;
    public WebhookCreatorLabelTests(ITestOutputHelper output) => _out = output;

    [Theory]
    [InlineData("", "https://discord.com/api/webhooks/1/x", "Enter name")]
    [InlineData("probe", "https://discord.com/api/webhooks", "Enter valid webhook")]
    [InlineData("probe", "https://discord.com/api/webhooks/0/probe", "Save")]
    public void TheLabelNamesTheFirstThingThatIsWrong(string name, string url, string expected)
    {
        var actual = WebhookCreatorView.SubmitLabel(name, url);
        _out.WriteLine($"{name,-8} {url,-46} -> {actual}");
        Assert.Equal(expected, actual);
    }

    [Theory]
    [InlineData("https://discord.com/api/webhooks/0/probe", true)]
    [InlineData("http://example.test/hook", true)]
    [InlineData("discord.com/api/webhooks", false)]
    [InlineData("", false)]
    public void OnlyAnAbsoluteHttpUrlCounts(string url, bool expected) =>
        Assert.Equal(expected, WebhookCreatorView.IsWebhookUrl(url));
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('WebhookCreatorLabelTests written')
