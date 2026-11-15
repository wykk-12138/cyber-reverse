import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

# 1) controls: add next to atcProxy
old_ctl = '''        var atcProxy = UiKit.Combo(atcProxyChoices, atcProxyIndex);

        var status = UiKit.Status();'''
new_ctl = '''        var atcProxy = UiKit.Combo(atcProxyChoices, atcProxyIndex);

        // R207: "Quicktask Settings" — measured from the running 5.18.32 build (Settings > General, between
        // "Default Delays" and "Shopify Settings") and backed by two locale keys that already existed:
        //   Settings.General.QuicktaskSettings  "Quicktask Settings"
        //   Settings.General.DefaultProfiles    "Default Profiles"
        //   Settings.General.DefaultProxies     "Default Proxies"
        // Both controls are single-select combos in the real window ("None" by default), and both fields already
        // existed on GlobalSettings (QuickTaskProfiles / QuickTaskProxies) with no UI to set them.
        var quickProfileChoices = new List<string> { "None" };
        quickProfileChoices.AddRange(services.Config.BillingGroups.Select(g => g.Name));
        var quickProfileIndex = Math.Max(0, quickProfileChoices.FindIndex(n =>
            string.Equals(n, s.QuickTaskProfiles.FirstOrDefault(), StringComparison.Ordinal)));
        var quickProfiles = UiKit.Combo(quickProfileChoices, quickProfileIndex);

        var quickProxyChoices = new List<string> { "None" };
        quickProxyChoices.AddRange(services.Config.ProxyGroups.Select(g => g.Name));
        var quickProxyIndex = Math.Max(0, quickProxyChoices.FindIndex(n =>
            string.Equals(n, services.Config.ProxyGroups.FirstOrDefault(g => g.Id == s.QuickTaskProxies)?.Name,
                StringComparison.Ordinal)));
        var quickProxies = UiKit.Combo(quickProxyChoices, quickProxyIndex);

        var status = UiKit.Status();'''
assert old_ctl in t, 'controls anchor'
t = t.replace(old_ctl, new_ctl)

# 2) save wiring: after the atcProxy assignment block
old_save = '''            // index 0 is the "(task proxy)" placeholder, so index-1 maps into the groups
            s.ShopifyBrowserProxy = atcProxy.SelectedIndex <= 0
                ? null
                : services.Config.ProxyGroups[Math.Min(atcProxy.SelectedIndex - 1,
                    services.Config.ProxyGroups.Count - 1)].Id;'''
new_save = '''            // index 0 is the "(task proxy)" placeholder, so index-1 maps into the groups
            s.ShopifyBrowserProxy = atcProxy.SelectedIndex <= 0
                ? null
                : services.Config.ProxyGroups[Math.Min(atcProxy.SelectedIndex - 1,
                    services.Config.ProxyGroups.Count - 1)].Id;

            // Quicktask defaults: index 0 is "None" on both, so index-1 maps into the group lists.
            s.QuickTaskProfiles = quickProfiles.SelectedIndex <= 0
                ? new List<string>()
                : new List<string> { quickProfiles.SelectedItem as string ?? string.Empty };
            s.QuickTaskProxies = quickProxies.SelectedIndex <= 0
                ? null
                : services.Config.ProxyGroups[Math.Min(quickProxies.SelectedIndex - 1,
                    services.Config.ProxyGroups.Count - 1)].Id;'''
assert old_save in t, 'save anchor'
t = t.replace(old_save, new_save)

# 3) the card itself, between Default Delays and Shopify Settings
old_card = '''            UiKit.PlainCard(
                new TextBlock { Text = "Shopify Settings", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },'''
new_card = '''            UiKit.PlainCard(
                new TextBlock { Text = "Quicktask Settings", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },
                UiKit.Row("Default Profiles", quickProfiles),
                UiKit.Row("Default Proxies", quickProxies)),
            UiKit.PlainCard(
                new TextBlock { Text = "Shopify Settings", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },'''
assert old_card in t, 'card anchor'
t = t.replace(old_card, new_card)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('patched GeneralSettingsView')
