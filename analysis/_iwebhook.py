import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Webhooks\IWebhook.cs"
t = '''using System.Collections.Generic;

namespace Cybersole.Core.Webhooks;

/// <summary>
/// What a webhook has to be able to do (IWebhook, R342).
///
/// <para>
/// The binding table carries six members on <c>Cybersole.Webhook.IWebhook</c>: Enabled, Events, ExtraFields, Name, Type
/// and Url. The replica had only ExtraFields, so the interface now states the whole contract and the concrete model
/// satisfies it. Where the extra fields are edited is still unknown (R341); where they are stored is not.
/// </para>
/// </summary>
public interface IWebhook
{
    /// <summary>The name shown in the list (bound as <c>Name</c>).</summary>
    string? Name { get; }

    /// <summary>Where the payload is posted (bound as <c>Url</c>).</summary>
    string Url { get; }

    /// <summary>Whether the hook fires at all (bound as <c>Enabled</c>).</summary>
    bool Enabled { get; }

    /// <summary>The platform the payload is shaped for (bound as <c>Type</c>).</summary>
    string Type { get; }

    /// <summary>Which notifications fire it (bound as <c>Events</c>).</summary>
    IReadOnlyList<string> Events { get; }

    /// <summary>Extra key/value pairs sent with every post (bound as <c>ExtraFields</c>).</summary>
    Dictionary<string, string> ExtraFields { get; }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('IWebhook: six members')

p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t2 = io.open(p2, encoding='utf-8').read()
old = '''    /// <summary>
    /// Extra key/value pairs posted alongside the payload (R318: the image binds IWebhook.ExtraFields and the locale has
    /// Settings.Webhook.ExtraFields, so the settings page has somewhere to put them).
    /// </summary>
    public Dictionary<string, string> ExtraFields { get; } = new();'''
new = '''    /// <summary>
    /// Extra key/value pairs posted alongside the payload (R318: the image binds IWebhook.ExtraFields and the locale has
    /// Settings.Webhook.ExtraFields, so the settings page has somewhere to put them).
    /// </summary>
    public Dictionary<string, string> ExtraFields { get; } = new();

    /// <summary>
    /// The platform the payload is shaped for (R342: bound as <c>IWebhook.Type</c>). Empty means "not chosen yet" —
    /// the "New Webhook" modal starts on a "Select provider" placeholder.
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// Which notifications fire this hook (R342: bound as <c>IWebhook.Events</c>). The five names are the locale's
    /// <c>Settings.Webhook.Event.*</c> keys: Checkouts, Declines, PayPal, PaymentRequests, SmartActions.
    /// </summary>
    public List<string> Events { get; } = new();'''
assert old in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
print('Webhook: Type + Events')
