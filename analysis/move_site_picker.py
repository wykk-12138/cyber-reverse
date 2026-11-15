import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs"
t = io.open(p, encoding="utf-8").read()

# The site picker moves into the More flyout: the locale files it under Proxies.More
# ("Test All On", "Select Site", "Test"), and the original's header line carries only
# Add Proxies / Clear All / More.
start = t.find("        // Proxies.More.TestAllOn + .SelectSite sit on the header line")
end = t.find("        actions.Children.Add(add);", start)
if start < 0 or end < 0:
    raise SystemExit("site-picker block not found")
t = t[:start] + t[end:]

# Build the site submenu where the flyout is assembled.
old_more = "        moreItems.Add(MoreItem(\"Clear Failed\", () => _grid?.ClearFailed()));"
new_more = '''        if (_sites.Count > 0 && _testOn is not null)
        {
            // Proxies.More.TestOn ("Test On:") over Proxies.More.SelectSite ("Select Site").
            var perSite = new List<object>();
            foreach (var site in _sites)
            {
                var chosen = site;
                perSite.Add(MoreItem(chosen, () => _ = _testOn(_urlForSite?.Invoke(chosen))));
            }

            moreItems.Add(new MenuItem
            {
                Header = "Test On:",
                ItemsSource = perSite,
            });
        }

        moreItems.Add(MoreItem("Clear Failed", () => _grid?.ClearFailed()));'''
if old_more not in t:
    raise SystemExit("more items anchor missing")
t = t.replace(old_more, new_more, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("site picker moved into the More flyout")
