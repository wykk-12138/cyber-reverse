import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- SizeCreatorView
size_start = t.find("/// <summary>\n/// Cybersole.Ui.Views.Settings.Modals.SizeCreatorView —")
size_end = t.find("/// <summary>Cybersole.Ui.Views.Settings.Modals.StoreCreatorView — Close / Save.</summary>")
if size_start < 0 or size_end < 0 or size_end <= size_start:
    raise SystemExit("size anchors: %d .. %d" % (size_start, size_end))

size_class = '''/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.SizeCreatorView.
///
/// <para>
/// R80 opened the live dialog; R83 moved the implementation here. It is not a size catalogue with a
/// Save button — it is a product lookup:
/// </para>
///
/// <code>
/// Add Custom Sizes
/// Enter product URL   [ https://cybersole.io/ ]  [Clear]
/// +---------------------------------------+
/// |        Nothing to see here            |
/// |     Search a valid product URL        |
/// +---------------------------------------+
/// [               Search                  ]
/// </code>
///
/// <para>
/// What the live dialog shows after a successful search was never captured, so the discovered
/// sizes are ticked to add them — the replica's own behaviour, kept rather than invented twice.
/// </para>
/// </summary>
public sealed class SizeCreatorView : SettingsModal
{
    public const string DialogTitle = "Add Custom Sizes";
    public const string Prompt = "Enter product URL";
    public const string EmptyTitle = "Nothing to see here";
    public const string EmptySubtitle = "Search a valid product URL";

    private readonly AppServices _services;
    private readonly Action? _onChanged;
    private readonly List<string> _discovered = new();
    private readonly StackPanel _found = new() { Spacing = 2 };
    private readonly Border _listHost;

    public SizeCreatorView(AppServices services, Action? onChanged = null) : base(DialogTitle, 620, 430)
    {
        _services = services;
        _onChanged = onChanged;

        var url = UiKit.Text(watermark: "https://cybersole.io/");
        var status = UiKit.Status();

        var empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 30),
            Children =
            {
                new TextBlock
                {
                    Text = EmptyTitle,
                    HorizontalAlignment = HorizontalAlignment.Center,
                    FontWeight = Avalonia.Media.FontWeight.SemiBold,
                },
                new TextBlock
                {
                    Text = EmptySubtitle,
                    HorizontalAlignment = HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };

        _listHost = new Border
        {
            MinHeight = 170,
            Padding = new Thickness(10),
            BorderThickness = new Thickness(1),
            BorderBrush = new Avalonia.Media.SolidColorBrush(
                Avalonia.Media.Color.Parse("#2A2E3A")),
            CornerRadius = new CornerRadius(6),
            Child = empty,
        };

        void ShowList()
        {
            _found.Children.Clear();
            foreach (var size in _discovered)
            {
                var target = size;
                var pick = UiKit.Check(size, false, on =>
                {
                    if (!on) return;
                    var sizes = services.Config.Settings.CustomSizes ??= new List<string>();
                    if (!sizes.Contains(target)) sizes.Add(target);
                    services.Config.Save();
                    _onChanged?.Invoke();
                    status.Text = target + " added.";
                });
                _found.Children.Add(pick);
            }

            _listHost.Child = _discovered.Count == 0 ? empty : _found;
        }

        ShowList();

        var search = new Button
        {
            Content = "Search",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            Padding = new Thickness(10, 8),
        };
        search.Click += async (_, _) => await SearchAsync(url, status).ConfigureAwait(true);

        var clear = UiKit.Button("Clear", () =>
        {
            url.Text = string.Empty;
            _discovered.Clear();
            ShowList();
            status.Text = string.Empty;
        });

        var promptRow = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto") };
        promptRow.Children.Add(new TextBlock
        {
            Text = Prompt,
            VerticalAlignment = VerticalAlignment.Center,
            Margin = new Thickness(0, 0, 10, 0),
        });
        Grid.SetColumn(url, 1);
        promptRow.Children.Add(url);
        Grid.SetColumn(clear, 2);
        promptRow.Children.Add(clear);

        Body.Children.Add(promptRow);
        Body.Children.Add(_listHost);
        Body.Children.Add(search);
        Body.Children.Add(status);

        // No BuildFooter: the live dialog has no Save/Close row, only the Search above.
    }

    /// <summary>
    /// Fetch the product page and pull out its variant titles. Size presets are Shopify only, so
    /// /products/{handle}.js is the right surface: it returns every variant with its public title.
    /// </summary>
    private async Task SearchAsync(TextBox urlBox, TextBlock status)
    {
        _discovered.Clear();
        _listHost.Child = null;

        var raw = urlBox.Text?.Trim();
        if (string.IsNullOrEmpty(raw)) { status.Text = EmptySubtitle; ShowList(); return; }

        if (!raw.StartsWith("http", StringComparison.OrdinalIgnoreCase)) raw = "https://" + raw;

        if (!Uri.TryCreate(raw, UriKind.Absolute, out var uri))
        {
            status.Text = EmptySubtitle;
            ShowList();
            return;
        }

        var handle = System.Text.RegularExpressions.Regex
            .Match(uri.AbsolutePath, @"/products/([^/?#]+)").Groups[1].Value;

        if (string.IsNullOrEmpty(handle))
        {
            status.Text = "That URL has no /products/{handle} segment.";
            ShowList();
            return;
        }

        status.Text = "Searching " + uri.Host + " ...";

        try
        {
            var res = await _services.Http.GetAsync(
                $"{uri.Scheme}://{uri.Host}/products/{handle}.js",
                new Cybersole.Http.RequestOptions { Tag = "custom-sizes-search" },
                CancellationToken.None).ConfigureAwait(true);

            if (!res.IsSuccess)
            {
                status.Text = $"Search failed: HTTP {res.StatusCode}";
                ShowList();
                return;
            }

            var parsed = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
            var variants = parsed["variants"] as Newtonsoft.Json.Linq.JArray;
            if (variants is null || variants.Count == 0)
            {
                status.Text = "That product has no variants.";
                ShowList();
                return;
            }

            foreach (var v in variants)
            {
                var title = v["public_title"]?.ToString() ?? v["title"]?.ToString();
                if (string.IsNullOrWhiteSpace(title) || title == "Default Title") continue;
                if (!_discovered.Contains(title)) _discovered.Add(title);
            }

            ShowList();
            status.Text = _discovered.Count == 0
                ? "No named sizes on that product."
                : $"{_discovered.Count} size(s) found. Tick the ones to keep.";
        }
        catch (Exception ex)
        {
            status.Text = "Search failed: " + ex.Message;
            ShowList();
        }
    }
}

'''

t = t[:size_start] + size_class + t[size_end:]

# ---------------------------------------------------------------- StoreCreatorView
store_start = t.find("/// <summary>Cybersole.Ui.Views.Settings.Modals.StoreCreatorView — Close / Save.</summary>")
store_end = t.find("/// <summary>Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView — Close / Save.</summary>")
if store_start < 0 or store_end < 0 or store_end <= store_start:
    raise SystemExit("store anchors: %d .. %d" % (store_start, store_end))

store_class = '''/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.StoreCreatorView.
///
/// <para>
/// R79 opened the live dialog and found one field and one button:
/// </para>
///
/// <code>
/// Add Custom Store
/// Enter store URL   [ https://cybersole.io/ ]
/// [                  Add                   ]
/// </code>
///
/// <para>
/// Name and Currency are not inputs because they are read off the URL — which is why the page's
/// table has three columns and this dialog has one field. R83 moved the implementation here so the
/// page and this class are not two copies of the same dialog.
/// </para>
/// </summary>
public sealed class StoreCreatorView : SettingsModal
{
    public const string DialogTitle = "Add Custom Store";
    public const string Prompt = "Enter store URL";

    public StoreCreatorView(AppServices services, Action? onAdded = null) : base(DialogTitle, 540, 260)
    {
        var url = UiKit.Text(watermark: "https://cybersole.io/");
        var status = UiKit.Status();

        var add = new Button
        {
            Content = "Add",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            Padding = new Thickness(10, 8),
        };

        add.Click += (_, _) =>
        {
            if (string.IsNullOrWhiteSpace(url.Text))
            {
                status.Text = "Enter store URL.";
                return;
            }

            var raw = url.Text!.Trim();
            if (!raw.StartsWith("http", StringComparison.OrdinalIgnoreCase)) raw = "https://" + raw;

            if (!Uri.TryCreate(raw, UriKind.Absolute, out var uri) || string.IsNullOrEmpty(uri.Host))
            {
                status.Text = "That is not a valid URL.";
                return;
            }

            var list = services.Config.Settings.CustomStores ??= new List<CustomStore>();
            list.Add(new CustomStore
            {
                Url = uri.ToString(),
                Name = uri.Host.Replace("www.", string.Empty, StringComparison.OrdinalIgnoreCase),
                Currency = "USD",
            });
            services.Config.Save();

            onAdded?.Invoke();
            Close();
        };

        Body.Children.Add(UiKit.Row(Prompt, url, 130));
        Body.Children.Add(add);
        Body.Children.Add(status);

        // No BuildFooter: the live dialog's only button is the full-width Add above.
    }
}

'''

t = t[:store_start] + store_class + t[store_end:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("both modals rewritten to the live dialogs")
