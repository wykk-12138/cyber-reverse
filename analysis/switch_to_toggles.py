import io

# ---------------------------------------------------------------- 1) UiKit.Switch
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\UiKit.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    public static ScrollViewer Scroll(Control content) => new()"
helper = '''    /// <summary>
    /// A labelled switch: the caption on the left, the green toggle hard right.
    ///
    /// <para>
    /// R78: the live Notifications and Keyboard Shortcuts pages are built out of switches, not
    /// checkboxes — every one of "Enable Notifications", "Allow … Notifications", "In-Bot
    /// Notifications", "Desktop Notifications" and "Sounds" is a toggle on the far right edge.
    /// <see cref="Check"/> draws a checkbox next to its caption, which is a different control in a
    /// different place.
    /// </para>
    /// </summary>
    public static Control Switch(string caption, bool value, Action<bool>? onChanged = null)
    {
        var toggle = new ToggleSwitch
        {
            IsChecked = value,
            OnContent = string.Empty,
            OffContent = string.Empty,
            VerticalAlignment = VerticalAlignment.Center,
            HorizontalAlignment = HorizontalAlignment.Right,
        };

        if (onChanged is not null)
            toggle.IsCheckedChanged += (_, _) => onChanged(toggle.IsChecked == true);

        var row = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        row.Children.Add(new TextBlock
        {
            Text = caption,
            VerticalAlignment = VerticalAlignment.Center,
        });
        Grid.SetColumn(toggle, 1);
        row.Children.Add(toggle);
        return row;
    }

'''
if anchor not in t:
    raise SystemExit("UiKit anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, helper + anchor, 1))
print("UiKit.Switch added")

# ---------------------------------------------------------------- 2) NotificationsView uses it
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t2 = io.open(p2, encoding="utf-8").read()

old_master = '''        var enabled = UiKit.Check("Enable Notifications", s.Notifications);
        enabled.IsCheckedChanged += (_, _) =>
        {
            s.Notifications = enabled.IsChecked == true;
            services.Config.Save();
            status.Text = s.Notifications ? "Notifications enabled." : "Notifications disabled.";
        };'''
new_master = '''        var master = UiKit.Switch("Enable Notifications", s.Notifications, on =>
        {
            s.Notifications = on;
            services.Config.Save();
            status.Text = on ? "Notifications enabled." : "Notifications disabled.";
        });'''
if old_master not in t2:
    raise SystemExit("master switch anchor missing")
t2 = t2.replace(old_master, new_master, 1)
t2 = t2.replace("UiKit.PlainCard(enabled),", "UiKit.PlainCard(master),", 1)

old_tab = '''        var allow = UiKit.Check(AllowLabel(tab), options.Enabled);
        var centre = UiKit.Check("In-Bot Notifications", options.Centre);
        var desktop = UiKit.Check("Desktop Notifications", options.Desktop);
        var sound = UiKit.Check("Sounds", options.Sound);

        void Save()
        {
            options.Enabled = allow.IsChecked == true;
            options.Centre = centre.IsChecked == true;
            options.Desktop = desktop.IsChecked == true;
            options.Sound = sound.IsChecked == true;
            services.Config.Save();
        }

        allow.IsCheckedChanged += (_, _) => Save();
        centre.IsCheckedChanged += (_, _) => Save();
        desktop.IsCheckedChanged += (_, _) => Save();
        sound.IsCheckedChanged += (_, _) => Save();'''

new_tab = '''        // Every one of these is a switch on the live page, not a checkbox.
        var allow = UiKit.Switch(AllowLabel(tab), options.Enabled, on =>
        {
            options.Enabled = on;
            services.Config.Save();
        });
        var centre = UiKit.Switch("In-Bot Notifications", options.Centre, on =>
        {
            options.Centre = on;
            services.Config.Save();
        });
        var desktop = UiKit.Switch("Desktop Notifications", options.Desktop, on =>
        {
            options.Desktop = on;
            services.Config.Save();
        });
        var sound = UiKit.Switch("Sounds", options.Sound, on =>
        {
            options.Sound = on;
            services.Config.Save();
        });'''

if old_tab not in t2:
    raise SystemExit("tab switches anchor missing")
t2 = t2.replace(old_tab, new_tab, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("NotificationsView switched to toggles")
