import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

old = '''    public WebhookCreatorView(AppServices services) : base("New webhook", 500, 400)
    {
        var name = UiKit.Text(watermark: "Checkout notifications");
        var url = UiKit.Text(watermark: "https://discord.com/api/webhooks/…");
        var platform = UiKit.Combo(new[] { "Discord", "Custom" });'''
new = '''    public WebhookCreatorView(AppServices services) : base("New Webhook", 500, 400)
    {
        // R339: the live "New Webhook" modal puts Name and Platform side by side, then the URL under a "Webhook"
        // heading; the placeholders are "Personal server", "Select provider" and the Discord URL itself.
        var name = UiKit.Text(watermark: "Personal server");
        var url = UiKit.Text(watermark: "https://discord.com/api/webhooks");
        var platform = UiKit.Combo(new[] { "Select provider", "Discord", "Custom" });'''
assert old in t
t = t.replace(old, new, 1)

old_rows = '''        Body.Children.Add(UiKit.Row("Name", name));
        Body.Children.Add(UiKit.Row("Webhook URL", url));
        Body.Children.Add(UiKit.Row("Platform", platform));'''
new_rows = '''        // Name and Platform share a row on the live modal; the URL sits below them under its own caption.
        var pair = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*") };
        pair.Children.Add(UiKit.Row("Name", name));
        var platformRow = UiKit.Row("Platform", platform);
        Grid.SetColumn(platformRow, 2);
        pair.Children.Add(platformRow);

        Body.Children.Add(pair);
        Body.Children.Add(UiKit.Caption("Webhook"));
        Body.Children.Add(url);'''
assert old_rows in t
t = t.replace(old_rows, new_rows, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('webhook modal relaid out')
