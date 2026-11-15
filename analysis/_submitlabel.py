import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

old = '''    public WebhookCreatorView(AppServices services) : base("New Webhook", 500, 400)'''
new = '''    /// <summary>
    /// The submit button's text, measured on the running build (R340): it names the first thing that is wrong —
    /// <c>Enter name</c> while the name is empty, <c>Enter valid webhook</c> while the URL does not parse, and
    /// <c>Save</c> once both are good. The button is only enabled in the last state.
    /// </summary>
    public static string SubmitLabel(string? name, string? url)
    {
        if (string.IsNullOrWhiteSpace(name)) return "Enter name";
        if (!IsWebhookUrl(url)) return "Enter valid webhook";
        return "Save";
    }

    /// <summary>True when the text is an absolute http(s) URL — what the live form accepts before enabling Save.</summary>
    public static bool IsWebhookUrl(string? url) =>
        !string.IsNullOrWhiteSpace(url)
        && Uri.TryCreate(url.Trim(), UriKind.Absolute, out var uri)
        && (uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps);

    public WebhookCreatorView(AppServices services) : base("New Webhook", 500, 400)'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SubmitLabel + IsWebhookUrl added')
