import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\MainWindow.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    private Control BuildProxies()")
end = t.find("    private Control BuildCheckouts()")
assert start > 0 and end > start, "anchors not found"

new_block = '''    private Control BuildProxies()
    {
        // R56: this was a ListBox over ProxyLines — "[Group 1] (12) behaviour=RoundRobin" plus one
        // indented line per proxy.
        //
        // R72: the page is what the original is — PROXY GROUPS on the left with a count badge per
        // group, one group at a time on the right. That is also what makes "Clear Over" honest: a
        // flat list cannot say which group's MaxUsage governs a row, and R56 had to guess.
        var sites = _vm.Services.Stores.Modules.Select(m => m.Name).Distinct().OrderBy(n => n).ToList();

        var page = new ProxyView(_vm.ProxyGroups, () =>
        {
            _vm.Services.Config.Save();
            _vm.RefreshProxies();
        })
            .WithTester(proxy => _vm.TestProxyAsync(proxy))
            .WithTestAll(async () => await _vm.TestProxiesAsync())
            .WithSites(sites, SiteUrl, url => _vm.TestProxiesAsync(url))
            .WithMover((proxy, from) =>
            {
                ProxyMoveView.Show(this, proxy, _vm.ProxyGroups, from, () =>
                {
                    _vm.Services.Config.Save();
                    _vm.RefreshProxies();
                });
                return Task.CompletedTask;
            })
            .WithImporter(group => ImportProxiesInto(group));

        _proxyPage = page;
        return page;
    }

    private ProxyView? _proxyPage;

    /// <summary>
    /// "Add Proxies" — <c>ProxyCreator.Title</c> / <c>.Label</c> / <c>.Placeholder</c> /
    /// <c>.DragDrop</c> / <c>.ImportFormat</c>, the same dialog shape as Add Accounts.
    /// </summary>
    private bool ImportProxiesInto(ProxyGroup group)
    {
        var box = new TextBox
        {
            AcceptsReturn = true,
            Height = 220,
            Watermark = "Enter proxies as ip:port:username:password",
            FontFamily = new Media.FontFamily("Consolas,monospace"),
        };
        var status = new TextBlock { Opacity = 0.8 };

        var body = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                new TextBlock { Text = group.Name, FontWeight = Media.FontWeight.SemiBold },
                new TextBlock { Text = "Proxies" },
                box,
                new TextBlock { Text = "Or drag and drop a .txt file here", Opacity = 0.7 },
                status,
            },
        };

        var import = new Button { Padding = new Thickness(16, 5) };
        import.Content = "Import (0) New Proxies";
        box.TextChanged += (_, _) =>
            import.Content = $"Import ({ImportParser.ParseProxies(box.Text).Count}) New Proxies";

        import.Click += (_, _) =>
        {
            var parsed = ImportParser.ParseProxies(box.Text);
            var added = 0;
            foreach (var proxy in parsed)
            {
                proxy.GroupId = group.Id;
                group.Proxies.Add(proxy);
                added++;
            }

            status.Text = $"Imported {added}.";
            if (added > 0 && TopLevel.GetTopLevel(this) is Window window) window.Close();
        };

        var opened = ViewHostModal.Show(this, "Add Proxies", UiKit.Scroll(body), 560, 460, import);
        if (opened)
        {
            _vm.Services.Config.Save();
            _vm.RefreshProxies();
        }
        return opened;
    }

    /// <summary>
    /// The origin of the site picked in "Test All On", or null for the neutral echo.
    /// </summary>
    /// <remarks>
    /// Taken from the module's first claimed domain rather than its display name: the name is a
    /// label ("Nike US") and the domain is what a request can actually be sent to.
    /// </remarks>
    private string? SiteUrl(string name)
    {
        var module = _vm.Services.Stores.Modules.FirstOrDefault(m => m.Name == name);
        var domain = module?.Domains.FirstOrDefault();
        return string.IsNullOrWhiteSpace(domain) ? null : $"https://{domain}/";
    }

'''

t = t[:start] + new_block + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("rewrote BuildProxies")
