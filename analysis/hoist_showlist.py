import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding="utf-8").read()

# ShowList was a local function in the constructor but SearchAsync is a method — hoist it.
old_fields = '''    private readonly StackPanel _found = new() { Spacing = 2 };
    private readonly Border _listHost;'''
new_fields = '''    private readonly StackPanel _found = new() { Spacing = 2 };
    private readonly StackPanel _empty;
    private readonly Border _listHost;
    private readonly TextBlock _status = UiKit.Status();'''
if old_fields not in t:
    raise SystemExit("fields anchor missing")
t = t.replace(old_fields, new_fields, 1)

old_empty = '''        var empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 30),
            Children =
            {
                new TextBlock
                {
                    Text = EmptyTitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = Avalonia.Media.FontWeight.SemiBold,
                },
                new TextBlock
                {
                    Text = EmptySubtitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };'''
new_empty = '''        _empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 30),
            Children =
            {
                new TextBlock
                {
                    Text = EmptyTitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = Avalonia.Media.FontWeight.SemiBold,
                },
                new TextBlock
                {
                    Text = EmptySubtitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };'''
if old_empty not in t:
    raise SystemExit("empty anchor missing")
t = t.replace(old_empty, new_empty, 1)

t = t.replace('            Child = empty,\n        };', '            Child = _empty,\n        };', 1)

old_local = '''        void ShowList()
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

        ShowList();'''
new_local = '''        ShowList();'''
if old_local not in t:
    raise SystemExit("local function anchor missing")
t = t.replace(old_local, new_local, 1)

# the hoisted method, appended before SearchAsync
anchor = '''    /// <summary>
    /// Fetch the product page and pull out its variant titles. Size presets are Shopify only, so
    /// /products/{handle}.js is the right surface: it returns every variant with its public title.
    /// </summary>'''
method = '''    /// <summary>Renders the discovered sizes, or the empty pane when there are none.</summary>
    private void ShowList()
    {
        _found.Children.Clear();
        foreach (var size in _discovered)
        {
            var target = size;
            var pick = UiKit.Check(size, false, on =>
            {
                if (!on) return;
                var sizes = _services.Config.Settings.CustomSizes ??= new List<string>();
                if (!sizes.Contains(target)) sizes.Add(target);
                _services.Config.Save();
                _onChanged?.Invoke();
                _status.Text = target + " added.";
            });
            _found.Children.Add(pick);
        }

        _listHost.Child = _discovered.Count == 0 ? _empty : _found;
    }

'''
if anchor not in t:
    raise SystemExit("search doc anchor missing")
t = t.replace(anchor, method + anchor, 1)

# SearchAsync's local `status` parameter is the ctor's; keep the signature but use the field.
t = t.replace("search.Click += async (_, _) => await SearchAsync(url, status).ConfigureAwait(true);",
              "search.Click += async (_, _) => await SearchAsync(url, status).ConfigureAwait(true);")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ShowList hoisted to a method")
