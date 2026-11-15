import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''public sealed class WebhookView : UserControl
{'''
add = '''public sealed class WebhookView : UserControl
{
    /// <summary>
    /// The extra payload fields a webhook can carry, in the order the locale lists them (R341).
    ///
    /// <para>
    /// Evidence is five dictionary keys in the image: <c>Settings.Webhook.ExtraFields</c> plus
    /// <c>Settings.Webhook.Extra.Email</c>, <c>.Price</c>, <c>.CheckoutProxy</c> and <c>.ProxyGroup</c>, whose English
    /// values are the labels below. The "New Webhook" modal does <b>not</b> show them (R340 walked all three submit
    /// states with Platform = Discord and no extra row appeared), so where they are toggled is still unknown — this
    /// constant records what exists, not where it goes.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> ExtraFieldChoices = new[]
    {
        "Email", "Price", "Checkout Proxy", "Proxy Group",
    };
'''
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ExtraFieldChoices added')
