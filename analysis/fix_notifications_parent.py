import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            var body = new StackPanel
            {
                Spacing = 8,
                Margin = new Thickness(12),
                Children =
                {
                    tab == "Checkout" ? enabled : new TextBlock { Text = " " },
                    centre,
                    desktop,
                    sound,
                    UiKit.Row("Sound file", path),
                },
            };'''

new = '''            // R76: "Enable Notifications" is the page-level switch (above the tabs). The Checkout
            // tab has its own "Allow Checkout Notifications", which is a second control — sharing
            // one CheckBox between two parents is the defect R73 already caught once.
            var allowCheckout = UiKit.Check("Allow Checkout Notifications", target.Enabled);
            allowCheckout.IsCheckedChanged += (_, _) =>
            {
                target.Enabled = allowCheckout.IsChecked == true;
                services.Config.Save();
            };

            var body = new StackPanel
            {
                Spacing = 8,
                Margin = new Thickness(12),
                Children =
                {
                    tab == "Checkout" ? allowCheckout : new TextBlock { Text = " " },
                    centre,
                    desktop,
                    sound,
                    UiKit.Row("Sound file", path),
                },
            };'''

if old not in t:
    raise SystemExit("notifications body anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("Enable Notifications un-doubled")
