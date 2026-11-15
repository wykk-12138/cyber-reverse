import io, os
# 1) the interface the image carries, with the one member it binds
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Webhook\IWebhook.cs"
os.makedirs(os.path.dirname(p), exist_ok=True)
t = '''using System.Collections.Generic;

namespace Cybersole.Webhook;

/// <summary>
/// What a webhook has to be able to do (Cybersole.Webhook.IWebhook, R318).
///
/// <para>
/// The image binds one member here — ExtraFields — and the locale carries Settings.Webhook.ExtraFields, so the
/// concept is not invented: a webhook can carry additional key/value pairs beside its URL. The interface exists so the
/// settings page and the sender agree on that without depending on the concrete model.
/// </para>
/// </summary>
public interface IWebhook
{
    /// <summary>Extra key/value pairs sent with every post (bound as <c>ExtraFields</c>).</summary>
    Dictionary<string, string> ExtraFields { get; }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('IWebhook written')

# 2) the model implements it
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t2 = io.open(p2, encoding='utf-8').read()
old = '''    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Url { get; set; } = "https://discord.com/api/webhooks";
    public string? Name { get; set; }
    public bool Enabled { get; set; } = true;'''
new = '''    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Url { get; set; } = "https://discord.com/api/webhooks";
    public string? Name { get; set; }
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Extra key/value pairs posted alongside the payload (R318: the image binds IWebhook.ExtraFields and the locale has
    /// Settings.Webhook.ExtraFields, so the settings page has somewhere to put them).
    /// </summary>
    public Dictionary<string, string> ExtraFields { get; } = new();'''
assert old in t2
t2 = t2.replace(old, new, 1)
t2 = t2.replace('public sealed class Webhook', 'public sealed class Webhook : Cybersole.Webhook.IWebhook', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('Webhook implements IWebhook')
