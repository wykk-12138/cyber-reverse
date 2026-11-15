import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding="utf-8").read()

start_marker = "/// <summary>Custom sizes (Cybersole.Ui.Views.Settings.CustomSizesView).</summary>"
end_marker = "/// <summary>\n/// Custom stores (Cybersole.Ui.Views.Settings.CustomStoresView)."

start = t.find(start_marker)
end = t.find(end_marker)
if start < 0 or end < 0 or end <= start:
    raise SystemExit("anchors: %d .. %d" % (start, end))
if t.count(start_marker) != 1 or t.count(end_marker) != 1:
    raise SystemExit("anchors not unique")

new_class = '''/// <summary>
/// Custom sizes (Cybersole.Ui.Views.Settings.CustomSizesView).
///
/// <para>
/// R80 opened the live page's dialog. The page is the same shape as Custom Stores — a count, two
/// header buttons, one sortable column and an empty state — and "Add Size(s)" opens a modal:
/// </para>
///
/// <code>
/// Custom Sizes
/// Add custom Shopify size presets for easy access
/// 0 Custom Sizes                     [Clear Sizes]  [Add Size(s)]
/// [ ]  Name ⇅
///            Nothing to see here
///        Add some size presets to get started
///
/// Add Size(s) opens:
///   Add Custom Sizes
///   Enter product URL   [ https://cybersole.io/ ]  [Clear]
///   ┌─────────────────────────────────────────┐
///   │         Nothing to see here             │
///   │      Search a valid product URL         │
///   └─────────────────────────────────────────┘
///   [                Search                   ]
/// </code>
///
/// <para>
/// What the live dialog shows <i>after</i> a successful search was not captured, so the replica
/// keeps its own discovered-sizes list and its "Add Selected" button rather than inventing a
/// different one. The parts that were captured — the title, the prompt, the Clear button, the empty
/// state wording and the full-width Search — are exact.
/// </para>
/// </summary>
public sealed class CustomSizesView : UserControl
{
    /// <summary>The page's one sortable column.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name" };

    /// <summary>Words the modal prints before a search.</summary>
    public const string DialogTitle = "Add Custom Sizes";
    public const string DialogPrompt = "Enter product URL";
    public const string DialogEmptyTitle = "Nothing to see here";
    public const string DialogEmptySubtitle = "Search a valid product URL";

    /// <summary>The page's count caption. The live page says "Custom Sizes" even at zero.</summary>
    public static string CountCaption(int count) =>
        count + (count == 1 ? " Custom Size" : " Custom Sizes");

    public CustomSizesView(AppServices services)
    {
        var status = UiKit.Status();
        var sizes = new List<string>(services.Config.Settings.CustomSizes ?? new List<string>());

        var count = new TextBlock { Opacity = 0.7, VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        var header = new Grid { ColumnDefinitions = new ColumnDefinitions("34,1*") };
        var body = new StackPanel();
        var empty = EmptyPane("Nothing to see here", "Add some size presets to get started");

        var sortAscending = true;

        void Persist()
        {
            services.Config.Settings.CustomSizes = sizes;
            services.Config.Save();
        }

        void Refresh()
        {
            count.Text = CountCaption(sizes.Count);

            header.Children.Clear();
            header.Children.Add(new TextBlock { Text = "" });
            var head = new Button
            {
                Content = "Name " + (sortAscending ? "↑" : "↓"),
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(4, 0),
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                Opacity = 0.75,
            };
            head.Click += (_, _) => { sortAscending = !sortAscending; Refresh(); };
            Grid.SetColumn(head, 1);
            header.Children.Add(head);

            body.Children.Clear();
            foreach (var size in sortAscending ? sizes.OrderBy(x => x) : sizes.OrderByDescending(x => x))
            {
                var row = new Grid { ColumnDefinitions = new ColumnDefinitions("34,1*") };

                var check = new CheckBox { Margin = new Thickness(4, 0, 0, 0) };
                var target = size;
                check.IsCheckedChanged += (_, _) =>
                {
                    if (check.IsChecked == true) return;
                    sizes.Remove(target);
                    Persist();
                    Refresh();
                    status.Text = $"{target} removed.";
                };
                row.Children.Add(check);

                var cell = new TextBlock
                {
                    Text = size,
                    VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                    Margin = new Thickness(4, 4, 4, 4),
                };
                Grid.SetColumn(cell, 1);
                row.Children.Add(cell);

                body.Children.Add(row);
            }

            var any = sizes.Count > 0;
            header.IsVisible = any;
            body.IsVisible = any;
            empty.IsVisible = !any;
        }

        Refresh();

        // ---- the modal
        var addSizes = UiKit.Button("Add Size(s)", () =>
        {
            var owner = TopLevel.GetTopLevel(this) as Window;
            var productUrl = UiKit.Text(watermark: "https://cybersole.io/");
            var dialogStatus = UiKit.Status();
            var found = new StackPanel { Spacing = 4 };
            var discovered = new List<string>();

            var dialogEmpty = EmptyPane(DialogEmptyTitle, DialogEmptySubtitle);
            var listHost = new Border
            {
                MinHeight = 180,
                Padding = new Thickness(10),
                BorderThickness = new Thickness(1),
                BorderBrush = new SolidColorBrush(Color.Parse("#2A2E3A")),
                CornerRadius = new CornerRadius(6),
                Child = dialogEmpty,
            };

            void RefreshDialog()
            {
                found.Children.Clear();
                foreach (var size in discovered)
                {
                    var pick = new CheckBox { Content = size };
                    var target = size;
                    pick.IsCheckedChanged += (_, _) =>
                    {
                        if (pick.IsChecked != true) return;
                        if (!sizes.Contains(target)) sizes.Add(target);
                        Persist();
                        Refresh();
                        dialogStatus.Text = $"{target} added.";
                    };
                    found.Children.Add(pick);
                }

                listHost.Child = discovered.Count == 0 ? dialogEmpty : found;
            }

            RefreshDialog();

            // Fetch the product page and pull out its variant titles. Size presets are Shopify
            // only, so /products/{handle}.js is the right surface: it returns every variant with
            // its public title.
            async void Search()
            {
                discovered.Clear();
                RefreshDialog();

                var raw = productUrl.Text?.Trim();
                if (string.IsNullOrEmpty(raw)) { dialogStatus.Text = DialogEmptySubtitle; return; }

                if (!raw.StartsWith("http", StringComparison.OrdinalIgnoreCase)) raw = "https://" + raw;

                if (!Uri.TryCreate(raw, UriKind.Absolute, out var uri))
                {
                    dialogStatus.Text = DialogEmptySubtitle;
                    return;
                }

                var handle = System.Text.RegularExpressions.Regex
                    .Match(uri.AbsolutePath, @"/products/([^/?#]+)")
                    .Groups[1].Value;

                if (string.IsNullOrEmpty(handle))
                {
                    dialogStatus.Text = "That URL has no /products/{handle} segment.";
                    return;
                }

                dialogStatus.Text = "Searching " + uri.Host + " ...";

                try
                {
                    var res = await services.Http.GetAsync(
                        $"{uri.Scheme}://{uri.Host}/products/{handle}.js",
                        new Cybersole.Http.RequestOptions { Tag = "custom-sizes-search" },
                        CancellationToken.None).ConfigureAwait(true);

                    if (!res.IsSuccess)
                    {
                        dialogStatus.Text = $"Search failed: HTTP {res.StatusCode}";
                        return;
                    }

                    var parsed = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
                    var variants = parsed["variants"] as Newtonsoft.Json.Linq.JArray;
                    if (variants is null || variants.Count == 0)
                    {
                        dialogStatus.Text = "That product has no variants.";
                        return;
                    }

                    foreach (var v in variants)
                    {
                        var title = v["public_title"]?.ToString() ?? v["title"]?.ToString();
                        if (string.IsNullOrWhiteSpace(title) || title == "Default Title") continue;
                        if (!discovered.Contains(title)) discovered.Add(title);
                    }

                    RefreshDialog();
                    dialogStatus.Text = discovered.Count == 0
                        ? "No named sizes on that product."
                        : $"{discovered.Count} size(s) found. Tick the ones to keep.";
                }
                catch (Exception ex)
                {
                    dialogStatus.Text = "Search failed: " + ex.Message;
                }
            }

            var search = UiKit.Button("Search", Search);
            search.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch;
            search.HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center;

            var clearField = UiKit.Button("Clear", () =>
            {
                productUrl.Text = string.Empty;
                discovered.Clear();
                RefreshDialog();
                dialogStatus.Text = string.Empty;
            });

            var urlRow = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto") };
            urlRow.Children.Add(new TextBlock
            {
                Text = DialogPrompt,
                VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 10, 0),
            });
            Grid.SetColumn(productUrl, 1);
            urlRow.Children.Add(productUrl);
            Grid.SetColumn(clearField, 2);
            urlRow.Children.Add(clearField);

            var modal = new Window
            {
                Title = DialogTitle,
                Width = 620,
                Height = 430,
                CanResize = false,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Content = UiKit.Scroll(UiKit.Form(
                    new TextBlock { Text = DialogTitle, FontSize = 18, FontWeight = FontWeight.SemiBold },
                    urlRow,
                    listHost,
                    search,
                    dialogStatus)),
            };

            if (owner is null) modal.Show();
            else modal.ShowDialog(owner);
        });

        var clearSizes = UiKit.Button("Clear Sizes", () =>
        {
            sizes.Clear();
            Persist();
            Refresh();
            status.Text = "All size presets cleared.";
        });

        var actions = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Right,
            Children = { clearSizes, addSizes },
        };

        var topRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        topRow.Children.Add(count);
        Grid.SetColumn(actions, 1);
        topRow.Children.Add(actions);

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(topRow, header, body, empty),
            status));
    }

    /// <summary>The two-line empty state the live pages use, at both sizes.</summary>
    private static StackPanel EmptyPane(string title, string subtitle) => new()
    {
        Spacing = 4,
        Margin = new Thickness(0, 30),
        Children =
        {
            new TextBlock
            {
                Text = title,
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                FontWeight = FontWeight.SemiBold,
            },
            new TextBlock
            {
                Text = subtitle,
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                Opacity = 0.6,
            },
        },
    };
}

'''

t = t[:start] + new_class + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("CustomSizesView replaced")
