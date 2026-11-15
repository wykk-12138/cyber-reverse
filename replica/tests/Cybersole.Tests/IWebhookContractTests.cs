using System.Collections.Generic;
using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Core.Webhooks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R342: <c>IWebhook</c> against the binding table.
///
/// <para>
/// The image binds six members on <c>Cybersole.Webhook.IWebhook</c> — Enabled, Events, ExtraFields, Name, Type, Url — and
/// the replica had only ExtraFields, so the interface was completed and <see cref="Webhook"/> made to satisfy it. Two of
/// the six were being collected by the "New Webhook" form and then thrown away (the platform combo and the event
/// checkboxes); they are stored now.
/// </para>
/// </summary>
public sealed class IWebhookContractTests
{
    private readonly ITestOutputHelper _out;
    public IWebhookContractTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheContractIsTheSixMembersTheBindingTableNames()
    {
        var members = typeof(IWebhook).GetProperties().Select(p => p.Name).OrderBy(n => n).ToArray();
        _out.WriteLine(string.Join(", ", members));

        Assert.Equal(new[] { "Enabled", "Events", "ExtraFields", "Name", "Type", "Url" }, members);
    }

    [Fact]
    public void AWebhookSatisfiesEveryOneOfThem()
    {
        var webhook = new Webhook { Name = "n", Url = "https://example.test/hook", Type = "Discord" };
        webhook.Events.Add("Checkouts");
        webhook.ExtraFields["Price"] = "true";

        IWebhook contract = webhook;

        Assert.Equal("n", contract.Name);
        Assert.Equal("https://example.test/hook", contract.Url);
        Assert.True(contract.Enabled);
        Assert.Equal("Discord", contract.Type);
        Assert.Equal(new[] { "Checkouts" }, contract.Events);
        Assert.Equal("true", contract.ExtraFields["Price"]);
    }

    [Fact]
    public void TypeStartsEmptyBecauseTheFormStartsOnAPlaceholder()
    {
        Assert.Equal(string.Empty, new Webhook().Type);
        Assert.Empty(new Webhook().Events);
    }
}
