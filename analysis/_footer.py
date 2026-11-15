import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

old = '''        Body.Children.Add(pair);
        Body.Children.Add(UiKit.Caption("Webhook"));
        Body.Children.Add(url);
        Body.Children.Add(UiKit.Row("Attach to group", group));
        Body.Children.Add(UiKit.Row("Events", UiKit.Scroll(events)));

        BuildFooter(SaveButton(() =>'''
new = '''        Body.Children.Add(pair);
        Body.Children.Add(UiKit.Caption("Webhook"));
        Body.Children.Add(url);
        Body.Children.Add(UiKit.Row("Attach to group", group));
        Body.Children.Add(UiKit.Row("Events", UiKit.Scroll(events)));

        // R340: the footer button names the first missing input and only lights up in the last state, as measured.
        var submit = UiKit.Button(SubmitLabel(name.Text, url.Text), () => { });
        submit.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        void Relabel()
        {
            submit.Content = SubmitLabel(name.Text, url.Text);
            submit.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        }
        name.TextChanged += (_, _) => Relabel();
        url.TextChanged += (_, _) => Relabel();
        Relabel();

        var saveAction = SaveButton(() =>'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('footer button wired')
