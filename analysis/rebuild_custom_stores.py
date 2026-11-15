import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding="utf-8").read()

start_marker = "/// <summary>Custom stores (Cybersole.Ui.Views.Settings.CustomStoresView).</summary>"
end_marker = "/// <summary>\n/// Data (Cybersole.Ui.Views.Settings.DataView)"

start = t.find(start_marker)
end = t.find(end_marker)
if start < 0 or end < 0 or end <= start:
    raise SystemExit("anchors: %d .. %d" % (start, end))
if t.count(start_marker) != 1 or t.count(end_marker) != 1:
    raise SystemExit("anchors not unique")

new_class = '''/// <summary>
/// Custom stores (Cybersole.Ui.Views.Settings.CustomStoresView).
///
/// <para>
/// R79 read the live page and its dialog. The page is a table, not a form:
/// </para>
///
/// <code>
/// Custom Stores
/// Add custom Shopify store presets for easy access
/// 0 Presets                          [Clear Presets]  [Add Preset]
/// [ ]  Name ⇅      URL ⇅      Currency ⇅
///            Nothing to see here
///        Add some store presets to get started
/// </code>
///
/// <para>
/// "Add Preset" opens a modal titled <b>Add Custom Store</b> with exactly one field,
/// <c>Enter store URL</c>, and a full-width <c>Add</c> — Name and Currency are derived from the
/// URL, which is why they are columns rather than inputs.
/// </para>
/// </summary>
public sealed class CustomStoresView : UserControl
{
    /// <summary>The three sortable columns, in the live page's order.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name", "URL", "Currency" };

    /// <summary>The modal's one field caption.</summary>
    public const string DialogPrompt = "Enter store URL";

    /// <summary>The modal's title.</summary>
    public const string DialogTitle = "Add Custom Store";

    /// <summary>The page's count caption. The live page says "Presets" even at zero.</summary>
    public static string CountCaption(int count) => count + (count == 1 ? " Preset" : " Presets");

    public CustomStoresView(AppServices services)
    {
        var status = UiKit.Status();
        var stores = services.Config.Settings.CustomStores ?? new List<CustomStore>();

        var count = new TextBlock { Opacity = 0.7, VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        var header = new Grid { ColumnDefinitions = new ColumnDefinitions("34,1.3*,2.2*,1*") };
        var body = new StackPanel();
        var empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 40),
            Children =
            {
                new TextBlock
                {
                    Text = "Nothing to see here",
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = FontWeights.SemiBold,
                },
                new TextBlock
                {
                    Text = "Add some store presets to get started",
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };

        var sortColumn = "Name";
        var ascending = true;

        void Persist()
        {
            services.Config.Settings.CustomStores = stores;
            services.Config.Save();
        }

        void Refresh()
        {
            count.Text = CountCaption(stores.Count);

            header.Children.Clear();
            header.Children.Add(new TextBlock { Text = "" });
            for (var i = 0; i < Columns.Count; i++)
            {
                var column = Columns[i];
                var glyph = sortColumn == column ? (ascending ? " ↑" : " ↓") : " ⇅";
                var button = new Button
                {
                    Content = column + glyph,
                    Background = Brushes.Transparent,
                    BorderThickness = new Thickness(0),
                    Padding = new Thickness(4, 0),
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                    Opacity = 0.75,
                };
                button.Click += (_, _) =>
                {
                    if (sortColumn == column) ascending = !ascending;
                    else { sortColumn = column; ascending = true; }
                    Refresh();
                };
                Grid.SetColumn(button, i + 1);
                header.Children.Add(button);
            }

            var ordered = sortColumn switch
            {
                "URL" => ascending ? stores.OrderBy(s => s.Url) : stores.OrderByDescending(s => s.Url),
                "Currency" => ascending ? stores.OrderBy(s => s.Currency) : stores.OrderByDescending(s => s.Currency),
                _ => ascending ? stores.OrderBy(s => s.Name) : stores.OrderByDescending(s => s.Name),
            };

            body.Children.Clear();
            foreach (var store in ordered)
            {
                var row = new Grid { ColumnDefinitions = new ColumnDefinitions("34,1.3*,2.2*,1*") };

                var check = new CheckBox { Margin = new Thickness(4, 0, 0, 0) };
                var target = store;
                check.IsCheckedChanged += (_, _) =>
                {
                    if (check.IsChecked == true) return;
                    stores.Remove(target);
                    Persist();
                    Refresh();
                    status.Text = $"{target.Name} removed.";
                };
                row.Children.Add(check);

                var cells = new[] { store.Name, store.Url, store.Currency };
                for (var i = 0; i < cells.Length; i++)
                {
                    var cell = new TextBlock
                    {
                        Text = cells[i],
                        VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                        Margin = new Thickness(4, 4, 4, 4),
                        TextTrimming = TextTrimming.CharacterEllipsis,
                    };
                    Grid.SetColumn(cell, i + 1);
                    row.Children.Add(cell);
                }

                body.Children.Add(row);
            }

            var any = stores.Count > 0;
            header.IsVisible = any;
            body.IsVisible = any;
            empty.IsVisible = !any;
        }

        Refresh();

        // ---- the modal, exactly as the live page shows it: one field, one full-width button
        var addPreset = UiKit.Button("Add Preset", () =>
        {
            var owner = TopLevel.GetTopLevel(this) as Window;
            var url = UiKit.Text(watermark: "https://cybersole.io/");
            var dialogStatus = UiKit.Status();

            void Add()
            {
                if (string.IsNullOrWhiteSpace(url.Text))
                {
                    dialogStatus.Text = "Enter store URL.";
                    return;
                }

                var raw = url.Text!.Trim();
                if (!raw.StartsWith("http", StringComparison.OrdinalIgnoreCase)) raw = "https://" + raw;

                if (!Uri.TryCreate(raw, UriKind.Absolute, out var uri) || string.IsNullOrEmpty(uri.Host))
                {
                    dialogStatus.Text = "That is not a valid URL.";
                    return;
                }

                stores.Add(new CustomStore
                {
                    Url = uri.ToString(),
                    Name = uri.Host.Replace("www.", string.Empty, StringComparison.OrdinalIgnoreCase),
                    Currency = "USD",
                });
                Persist();
                Refresh();
                status.Text = $"{uri.Host} added.";
                (TopLevel.GetTopLevel(url) as Window)?.Close();
            }

            var add = UiKit.Button("Add", Add);
            add.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch;
            add.HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center;

            var modal = new Window
            {
                Title = DialogTitle,
                Width = 540,
                Height = 260,
                CanResize = false,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Content = UiKit.Scroll(UiKit.Form(
                    new TextBlock { Text = DialogTitle, FontSize = 18, FontWeight = FontWeights.SemiBold },
                    UiKit.Row(DialogPrompt, url, 130),
                    add,
                    dialogStatus)),
            };

            if (owner is null) modal.Show();
            else modal.ShowDialog(owner);
        });

        var clear = UiKit.Button("Clear Presets", () =>
        {
            stores.Clear();
            Persist();
            Refresh();
            status.Text = "All presets cleared.";
        });

        var actions = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Right,
            Children = { clear, addPreset },
        };

        var topRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        topRow.Children.Add(count);
        Grid.SetColumn(actions, 1);
        topRow.Children.Add(actions);

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(topRow, header, body, empty),
            status));
    }
}

'''

t = t[:start] + new_class + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("CustomStoresView replaced")
