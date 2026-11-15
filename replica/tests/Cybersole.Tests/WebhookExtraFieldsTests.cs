using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R341: what goes into <c>IWebhook.ExtraFields</c>, from the locale rather than from a screen.
///
/// <para>
/// R318 added <c>IWebhook.ExtraFields</c> on the strength of one locale key. R340 then walked every state of the live
/// "New Webhook" modal and no extra-field row appeared, which left the property looking invented. It is not: the image
/// carries five keys — <c>Settings.Webhook.ExtraFields</c> and four <c>Settings.Webhook.Extra.*</c> labels whose English
/// values are Email / Price / Checkout Proxy / Proxy Group. So the property is real; only its screen is unknown. This test
/// pins the four labels and keeps the dictionary on the model.
/// </para>
/// </summary>
public sealed class WebhookExtraFieldsTests
{
    private readonly ITestOutputHelper _out;
    public WebhookExtraFieldsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheFourExtraFieldLabelsAreTheLocaleValues()
    {
        _out.WriteLine(string.Join(" | ", WebhookView.ExtraFieldChoices));
        Assert.Equal(new[] { "Email", "Price", "Checkout Proxy", "Proxy Group" }, WebhookView.ExtraFieldChoices);
    }

    [Fact]
    public void AWebhookCarriesThemAsAKeyValueBag()
    {
        var webhook = new Webhook();
        webhook.ExtraFields["Email"] = "true";
        webhook.ExtraFields["Price"] = "false";

        Assert.Equal(2, webhook.ExtraFields.Count);
        Assert.Equal("true", webhook.ExtraFields["Email"]);
        Assert.IsAssignableFrom<Cybersole.Core.Webhooks.IWebhook>(webhook);
    }
}
