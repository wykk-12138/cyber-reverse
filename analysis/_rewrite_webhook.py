import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()
a = t.index('/// <summary>Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView')
b = t.index('/// <summary>\n/// Cybersole.Ui.Views.Settings.Modals.ShippingRatesCreatorView')

new = '''/// <summary>
/// The "New Webhook" form (Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView).
///
/// <para>
/// Laid out from the running 5.18.32 build (R339): Name and Platform share a row, the URL sits under a "Webhook"
/// caption, and the footer button names the first thing that is not right yet (R340) — "Enter name" while the name box
/// is empty, "Enter valid webhook" while the URL does not parse, "Save" once both are good, and only that last state is
/// enabled. All three labels were read off the live modal.
/// </para>
/// </summary>
public sealed class WebhookCreatorView : SettingsModal
{
    /// <summary>
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

    public WebhookCreatorView(AppServices services) : base("New Webhook", 500, 400)
    {
        var name = UiKit.Text(watermark: "Personal server");
        var url = UiKit.Text(watermark: "https://discord.com/api/webhooks");
        var platform = UiKit.Combo(new[] { "Select provider", "Discord", "Custom" });
        var group = UiKit.Combo(services.Config.TaskGroups.Select(g => g.Name).ToList());
        var events = new StackPanel { Spacing = 2 };
        foreach (var evt in new[] { "Checkouts", "Declines", "PayPal", "Payment requests", "Smart actions" })
            events.Children.Add(UiKit.Check(evt, true));

        // Name and Platform share a row on the live modal; the URL sits below them under its own caption.
        var pair = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*") };
        pair.Children.Add(UiKit.Row("Name", name));
        var platformRow = UiKit.Row("Platform", platform);
        Grid.SetColumn(platformRow, 2);
        pair.Children.Add(platformRow);

        Body.Children.Add(pair);
        Body.Children.Add(UiKit.Caption("Webhook"));
        Body.Children.Add(url);
        Body.Children.Add(UiKit.Row("Attach to group", group));
        Body.Children.Add(UiKit.Row("Events", UiKit.Scroll(events)));

        var save = SaveButton(() =>
        {
            if (!IsWebhookUrl(url.Text))
                throw new InvalidOperationException("A webhook URL is required.");

            var webhook = new Webhook
            {
                Name = string.IsNullOrWhiteSpace(name.Text) ? "Webhook" : name.Text!,
                Url = url.Text!,
            };
            services.Config.Settings.Webhooks.Add(webhook);

            var index = Math.Clamp(group.SelectedIndex, 0, Math.Max(0, services.Config.TaskGroups.Count - 1));
            if (services.Config.TaskGroups.Count > 0)
                services.Config.TaskGroups[index].Webhooks.Add(webhook);

            services.Config.Save();
        });

        BuildFooter(save);

        void Relabel()
        {
            save.Content = SubmitLabel(name.Text, url.Text);
            save.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        }
        name.TextChanged += (_, _) => Relabel();
        url.TextChanged += (_, _) => Relabel();
        Relabel();
    }
}

'''
io.open(p, 'w', encoding='utf-8', newline='').write(t[:a] + new + t[b:])
print('WebhookCreatorView rewritten wholesale')
