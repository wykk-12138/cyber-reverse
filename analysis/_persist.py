import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

# persist the event checkboxes and the chosen platform (both were collected but thrown away)
old = '''            var webhook = new Webhook
            {
                Name = string.IsNullOrWhiteSpace(name.Text) ? "Webhook" : name.Text!,
                Url = url.Text!,
            };'''
new = '''            var webhook = new Webhook
            {
                Name = string.IsNullOrWhiteSpace(name.Text) ? "Webhook" : name.Text!,
                Url = url.Text!,
                // R342: the platform combo and the event checkboxes were collected and then dropped; the binding
                // table says IWebhook carries both (Type, Events), so they are stored now.
                Type = platform.SelectedIndex > 0 && platform.SelectedItem is string chosen ? chosen : string.Empty,
            };

            foreach (var box in events.Children.OfType<CheckBox>())
                if (box.IsChecked == true && box.Content is string label)
                    webhook.Events.Add(label);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('events + type persisted')
