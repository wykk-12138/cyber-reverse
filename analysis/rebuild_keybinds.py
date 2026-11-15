import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- 1) Section lays out two per row
start = t.find("        Control Section(string title, string page, params (string Label, KeyBind Bind)[] binds)")
end = t.find("        var tasks = Section(\"Tasks\", \"Tasks\",")
if start < 0 or end < 0:
    raise SystemExit("Section helper not found")

new_section = '''        // R76: the live page puts two bindings on one row, each with its chord in a chip and an X
        // to clear it. One per row was the replica's own layout, and it fit only seven of the
        // twelve task chords — the other five had no row at all.
        Control Section(string title, string page, params (string Label, KeyBind Bind)[] binds)
        {
            var grid = new Grid
            {
                ColumnDefinitions = new ColumnDefinitions("150,Auto,Auto,24,150,Auto,Auto"),
            };

            for (var i = 0; i < binds.Length; i++)
            {
                var row = i / 2;
                var half = i % 2;
                var column = half == 0 ? 0 : 4;

                while (grid.RowDefinitions.Count <= row) grid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));

                var (label, bind) = binds[i];

                var text = new TextBlock
                {
                    Text = label,
                    VerticalAlignment = VerticalAlignment.Center,
                    Margin = new Thickness(0, 3, 8, 3),
                };
                Grid.SetRow(text, row);
                Grid.SetColumn(text, column);
                grid.Children.Add(text);

                var capture = new Button
                {
                    Content = Cybersole.Core.Input.KeyBindMatcher.Describe(bind),
                    MinWidth = 76,
                    HorizontalContentAlignment = HorizontalAlignment.Center,
                    Margin = new Thickness(0, 2, 4, 2),
                };

                capture.Click += (_, _) =>
                {
                    if (capturing?.Bind == bind) { EndCapture("Capture cancelled."); return; }

                    EndCapture(null);
                    capturing = (capture, bind, page, label);
                    capture.Content = "Press a key…";
                    capture.Focus();
                    status.Text = $"Listening for {page} · {label}. Esc cancels.";
                };

                Grid.SetRow(capture, row);
                Grid.SetColumn(capture, column + 1);
                grid.Children.Add(capture);
                pairs.Add((bind, capture));

                // The X clears the chord. The original shows one per binding, and "unbound" is a
                // state the matcher already understands — Key 0 matches nothing.
                if (half == 0 || true)
                {
                    var clear = new Button
                    {
                        Content = "✕",
                        Padding = new Thickness(4, 0),
                        Background = Brushes.Transparent,
                        BorderThickness = new Thickness(0),
                        Margin = new Thickness(0, 2, 16, 2),
                    };
                    var target = bind;
                    var shown = capture;
                    clear.Click += (_, _) =>
                    {
                        target.Key = 0;
                        target.Modifiers = 0;
                        shown.Content = Cybersole.Core.Input.KeyBindMatcher.Describe(target);
                        services.Config.Save();
                        status.Text = $"{page} · {label} cleared.";
                    };

                    Grid.SetRow(clear, row);
                    Grid.SetColumn(clear, column + 2);
                    grid.Children.Add(clear);
                }
            }

            return UiKit.PlainCard(new TextBlock
            {
                Text = title,
                Opacity = 0.6,
                Margin = new Thickness(0, 0, 0, 6),
            }, grid);
        }

'''

t = t[:start] + new_section + t[end:]

# ---------------------------------------------------------------- 2) the three tables, as printed
start2 = t.find('        var tasks = Section("Tasks", "Tasks",')
end2 = t.find("        // One handler on the page, not one per row")
if start2 < 0 or end2 < 0:
    raise SystemExit("section call sites not found")

tables = '''        var tasks = Section("Tasks", "Tasks",
            ("New Group", s.KeyBinds.Tasks.New),
            ("Task Creator", s.KeyBinds.Tasks.Creator),
            ("Task Editor", s.KeyBinds.Tasks.Editor),
            ("Start All", s.KeyBinds.Tasks.StartAll),
            ("Stop All", s.KeyBinds.Tasks.StopAll),
            ("Delete Selected", s.KeyBinds.Tasks.Delete),
            ("Clone Selected", s.KeyBinds.Tasks.Clone),
            ("Search", s.KeyBinds.Tasks.Search),
            ("Quicktask", s.KeyBinds.Tasks.Quicktask),
            ("Link Change", s.KeyBinds.Tasks.LinkChange),
            ("Next Group", s.KeyBinds.Tasks.NextGroup),
            ("Previous Group", s.KeyBinds.Tasks.PreviousGroup));

        var proxies = Section("Proxies", "Proxies",
            ("New Group", s.KeyBinds.Proxies.New),
            ("Add Proxies", s.KeyBinds.Proxies.Add),
            ("Test All", s.KeyBinds.Proxies.TestAll),
            ("Copy Selected", s.KeyBinds.Proxies.Copy),
            ("Clone Selected", s.KeyBinds.Proxies.Clone),
            ("Delete Selected", s.KeyBinds.Proxies.Delete));

        var billing = Section("Billing", "Billing",
            ("New Group", s.KeyBinds.Billing.New),
            ("Add Profile", s.KeyBinds.Billing.Add),
            ("Clone Selected", s.KeyBinds.Billing.Clone),
            ("Delete Selected", s.KeyBinds.Billing.Delete));

'''
t = t[:start2] + tables + t[end2:]

# ---------------------------------------------------------------- 3) the footer becomes the toggle
start3 = t.find("        Content = UiKit.Scroll(UiKit.Form(")
end3 = t.find("        // the capture buttons hold a snapshot of the text")
if start3 < 0 or end3 < 0:
    raise SystemExit("footer not found")

footer = '''        // The original's whole page-level control is one switch: "Enable Keyboard Shortcuts".
        // The replica had four buttons here (Enable / Disable / Reset / Save); the switch covers
        // the first two, and every edit now saves immediately, which is what the X and the capture
        // already did.
        var enabled = new ToggleSwitch
        {
            IsChecked = s.Keybinds,
            OnContent = string.Empty,
            OffContent = string.Empty,
            VerticalAlignment = VerticalAlignment.Center,
        };
        enabled.IsCheckedChanged += (_, _) =>
        {
            s.Keybinds = enabled.IsChecked == true;
            services.Config.Save();
            status.Text = s.Keybinds ? "Shortcuts enabled." : "Shortcuts disabled.";
        };

        var toggleRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        toggleRow.Children.Add(new TextBlock
            {
                Text = "Enable Keyboard Shortcuts",
                VerticalAlignment = VerticalAlignment.Center,
            });
        Grid.SetColumn(enabled, 1);
        toggleRow.Children.Add(enabled);

        Content = UiKit.Scroll(UiKit.Form(
            toggleRow,
            tasks,
            proxies,
            billing,
            status));

'''
t = t[:start3] + footer + t[end3:]

# ---------------------------------------------------------------- 4) AllOnPage matches the tables
start4 = t.find("    private static IEnumerable<(KeyBind Bind, string Label)> AllOnPage(GlobalSettings s, string page)")
end4 = t.find("    private static void Copy(TaskKeyBinds from, TaskKeyBinds to)")
if start4 < 0 or end4 < 0:
    raise SystemExit("AllOnPage not found")

allonpage = '''    /// <summary>
    /// Every chord on one page, with the label the page prints. The clash check reads this, so it
    /// has to list exactly what the table shows — R76 found it listing seven of twelve.
    /// </summary>
    private static IEnumerable<(KeyBind Bind, string Label)> AllOnPage(GlobalSettings s, string page)
    {
        return page switch
        {
            "Tasks" => new (KeyBind, string)[]
            {
                (s.KeyBinds.Tasks.New, "New Group"),
                (s.KeyBinds.Tasks.Creator, "Task Creator"),
                (s.KeyBinds.Tasks.Editor, "Task Editor"),
                (s.KeyBinds.Tasks.StartAll, "Start All"),
                (s.KeyBinds.Tasks.StopAll, "Stop All"),
                (s.KeyBinds.Tasks.Delete, "Delete Selected"),
                (s.KeyBinds.Tasks.Clone, "Clone Selected"),
                (s.KeyBinds.Tasks.Search, "Search"),
                (s.KeyBinds.Tasks.Quicktask, "Quicktask"),
                (s.KeyBinds.Tasks.LinkChange, "Link Change"),
                (s.KeyBinds.Tasks.NextGroup, "Next Group"),
                (s.KeyBinds.Tasks.PreviousGroup, "Previous Group"),
            },
            "Proxies" => new (KeyBind, string)[]
            {
                (s.KeyBinds.Proxies.New, "New Group"),
                (s.KeyBinds.Proxies.Add, "Add Proxies"),
                (s.KeyBinds.Proxies.TestAll, "Test All"),
                (s.KeyBinds.Proxies.Copy, "Copy Selected"),
                (s.KeyBinds.Proxies.Clone, "Clone Selected"),
                (s.KeyBinds.Proxies.Delete, "Delete Selected"),
            },
            _ => new (KeyBind, string)[]
            {
                (s.KeyBinds.Billing.New, "New Group"),
                (s.KeyBinds.Billing.Add, "Add Profile"),
                (s.KeyBinds.Billing.Clone, "Clone Selected"),
                (s.KeyBinds.Billing.Delete, "Delete Selected"),
            },
        };
    }

'''
t = t[:start4] + allonpage + t[end4:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("KeyBindsView rebuilt to the live table")
