using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Layout;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Services;
using Cybersole.Services.Mail;
using Cybersole.Stores.Payments;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Settings;

/// <summary>
/// A small table for the three account pages: a clickable header row, one row per record, and the
/// two-line empty state the live pages print.
///
/// <para>
/// R84: the three pages had a <see cref="ListBox"/> of formatted strings and nothing else — no
/// columns, and a single-line empty state. The live pages are tables, and the columns came off the
/// running build in R75 (Host / Email / Inbox Count, Name / Email, Email / Status); the binary's
/// locale carries the same sets as <c>Settings.Google.Header.*</c> and
/// <c>Settings.PayPal.Header.*</c>.
/// </para>
///
/// <para>
/// R85: the headers said <c>⇅</c> and did nothing — a dead affordance of exactly the kind
/// <c>DeadButtonTests</c> exists to catch. They are buttons now, and clicking one sorts by that
/// column, toggling ascending/descending, with the glyph following (<c>↑</c> / <c>↓</c> / <c>⇅</c>).
/// </para>
/// </summary>
public sealed class AccountTable : UserControl
{
    private readonly Grid _header = new();
    private readonly StackPanel _body = new();
    private readonly StackPanel _empty;
    private readonly string _columnTemplate;
    private readonly List<Button> _headers = new();

    private int _sortColumn = -1;
    private bool _ascending = true;

    public AccountTable(IReadOnlyList<string> columns, string emptyTitle, string emptySubtitle)
    {
        Columns = columns;
        _columnTemplate = "34," + string.Join(",", columns.Select(_ => "1*"));

        _header.ColumnDefinitions = new ColumnDefinitions(_columnTemplate);
        _header.Children.Add(new TextBlock { Text = string.Empty });

        for (var i = 0; i < columns.Count; i++)
        {
            var index = i;
            var head = new Button
            {
                Content = columns[i] + " ⇅",
                Background = Avalonia.Media.Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(4, 0),
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Left,
                Opacity = 0.7,
            };
            head.Click += (_, _) => SortBy(index);
            Grid.SetColumn(head, i + 1);
            _header.Children.Add(head);
            _headers.Add(head);
        }

        _empty = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 30),
            Children =
            {
                new TextBlock
                {
                    Text = emptyTitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = Avalonia.Media.FontWeight.SemiBold,
                },
                new TextBlock
                {
                    Text = emptySubtitle,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    Opacity = 0.6,
                },
            },
        };

        Content = new StackPanel { Spacing = 2, Children = { _header, _body, _empty } };
        Rows = Array.Empty<string[]>();
    }

    /// <summary>The column captions, in order.</summary>
    public IReadOnlyList<string> Columns { get; }

    /// <summary>The selected row, or -1.</summary>
    public int SelectedIndex { get; private set; } = -1;

    /// <summary>Which column the rows are ordered by, or -1 for as-given.</summary>
    public int SortColumn => _sortColumn;

    /// <summary>True when the current sort is ascending.</summary>
    public bool SortAscending => _ascending;

    private string[][] _rows = Array.Empty<string[]>();

    /// <summary>Replaces the rows and repaints. An empty array shows the empty state.</summary>
    public string[][] Rows
    {
        get => _rows;
        set
        {
            _rows = value;
            SelectedIndex = value.Length == 0 ? -1 : Math.Clamp(SelectedIndex, -1, value.Length - 1);
            Repaint();
        }
    }

    /// <summary>Selects a row index (or -1).</summary>
    public void Select(int index)
    {
        SelectedIndex = index >= 0 && index < _rows.Length ? index : -1;
        Repaint();
    }

    /// <summary>
    /// Orders by <paramref name="column"/>: the first click sorts ascending, a second click on the
    /// same column reverses it. Ordinal comparison — these are hostnames, addresses and counts, not
    /// prose.
    /// </summary>
    public void SortBy(int column)
    {
        if (column < 0 || column >= Columns.Count) return;

        if (_sortColumn == column) _ascending = !_ascending;
        else { _sortColumn = column; _ascending = true; }

        Repaint();
    }

    /// <summary>The rows in display order — what the body actually shows.</summary>
    public string[][] Ordered()
    {
        if (_sortColumn < 0) return _rows;

        var column = _sortColumn;
        var ordered = _ascending
            ? _rows.OrderBy(r => Cell(r, column), StringComparer.Ordinal)
            : _rows.OrderByDescending(r => Cell(r, column), StringComparer.Ordinal);

        return ordered.ToArray();
    }

    private static string Cell(string[] row, int column) =>
        column >= 0 && column < row.Length ? row[column] ?? string.Empty : string.Empty;

    private void Repaint()
    {
        for (var i = 0; i < _headers.Count; i++)
        {
            var glyph = _sortColumn == i ? (_ascending ? " ↑" : " ↓") : " ⇅";
            _headers[i].Content = Columns[i] + glyph;
        }

        _body.Children.Clear();

        var rows = Ordered();
        for (var r = 0; r < rows.Length; r++)
        {
            var index = r;
            var row = new Grid
            {
                ColumnDefinitions = new ColumnDefinitions(_columnTemplate),
                Background = r == SelectedIndex
                    ? new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#1C2330"))
                    : Avalonia.Media.Brushes.Transparent,
            };

            var check = new CheckBox { IsChecked = r == SelectedIndex, Margin = new Thickness(4, 0, 0, 0) };
            check.IsCheckedChanged += (_, _) =>
            {
                if (check.IsChecked == true) Select(index);
            };
            row.Children.Add(check);

            for (var c = 0; c < rows[r].Length && c < Columns.Count; c++)
            {
                var cell = new TextBlock
                {
                    Text = rows[r][c],
                    VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                    Margin = new Thickness(4, 4, 4, 4),
                    TextTrimming = Avalonia.Media.TextTrimming.CharacterEllipsis,
                };
                Grid.SetColumn(cell, c + 1);
                row.Children.Add(cell);
            }

            _body.Children.Add(row);
        }

        var any = rows.Length > 0;
        _header.IsVisible = any;
        _body.IsVisible = any;
        _empty.IsVisible = !any;
    }
}

/// <summary>General settings (Cybersole.Ui.Views.Settings.GeneralSettingsView).</summary>
public sealed class GeneralSettingsView : UserControl
{
    private readonly AppServices? _generalServices;

    /// <summary>
    /// Every profile the user has, flattened across the profile groups (bound as <c>ProfileItems</c>).
    ///
    /// <para>
    /// Evidence: <c>docs/xaml_bindings.json</c> has <c>GeneralSettingsView.ProfileItems!Getter</c>
    /// (descriptor at <c>analysis/pe_strings.txt</c> 0x03216368) and the same member on
    /// <c>TaskCreatorMainView</c> (0x032215e9); the original also has a <c>Models.ProfileItem</c> with a
    /// <c>Name</c>. Both pages therefore read the same profile list, which is what the replica's task
    /// creator already exposes — this is that list, on the page that was missing it. Whether the
    /// general page shows it as a picker or a count is not established, so nothing is laid out.
    /// </para>
    /// </summary>
    public IReadOnlyList<Profile> ProfileItems =>
        _generalServices?.Config.BillingGroups.SelectMany(g => g.Profiles).ToList() ?? new List<Profile>();

    public GeneralSettingsView(AppServices services)
    {
        _generalServices = services;
        var s = services.Config.Settings;

        // R757: the live pane prints "2,500 ms" and "10 sec". The boxes hold the bare numbers -- that is what the
        // live fields report as their value -- so the units are added at the layout site, not here, and these stay
        // TextBox so the readers below keep compiling.
        var monitor = UiKit.Number(s.MonitorDelay);
        var retry = UiKit.Number(s.RetryDelay);
        var timeout = UiKit.Number(s.Timeout);
        // Four choices, matching the four resource keys the live build carries.
        var languageSvc = new Cybersole.Services.Localization.LocalizationService(s);
        var language = UiKit.Combo(
            Cybersole.Services.Localization.LocalizationService.DisplayNames.ToList(),
            languageSvc.CurrentIndex);
        var currency = UiKit.Combo(Enum.GetNames<Core.Models.Currency>(),
            (int)s.Currency);
        var startup = UiKit.Combo(Enum.GetNames<StartupPage>(), (int)s.StartupPage);
        var queue = UiKit.Combo(Enum.GetNames<QueuePresentation>(), (int)s.QueuePresentation);
        var clock = UiKit.Number(s.Clock);
        var enableClock = UiKit.Check("Enable clock", s.EnableClock);
        var clockFormat = UiKit.Text(s.ClockFormat, watermark: "HH:mm");

        var concMode = UiKit.Combo(Enum.GetNames<ConcurrencyMode>(), (int)s.MonitorConcurrency.Mode);
        var concMax = UiKit.Number(s.MonitorConcurrency.Maximum);
        var concRatio = UiKit.Text(s.MonitorConcurrency.Ratio.ToString("0.##"));

        // R51: two halves of one setting, each orphaned.
        //
        //   locale:            Settings.General.ATCBrowserProxy  "ATC Browser Proxy"
        //   GlobalSettings:    ShopifyBrowserProxy { get; set; }   <- no reader, no control
        //
        // The locale label has no field (one of the eight found in round 198) and the field has
        // no label. They are the same setting: which proxy group add-to-cart goes through. The
        // field is a string, which is a group id rather than a flag.
        //
        // Wired as a choice, not as a behaviour change — nothing reads it yet, so a value stored
        // here has no effect. That is deliberate: the selector can be added safely, while making
        // add-to-cart swap proxies is a behavioural change that needs the original's own evidence
        // for when it applies (always? only when the task proxy is burned?).
        var atcProxyChoices = services.Config.ProxyGroups.Select(g => g.Name)
            .DefaultIfEmpty("(task proxy)").ToList();
        var atcProxyIndex = Math.Max(0, atcProxyChoices.FindIndex(n => string.Equals(n,
            services.Config.ProxyGroups.FirstOrDefault(g => g.Id == s.ShopifyBrowserProxy)?.Name,
            StringComparison.Ordinal)));
        var atcProxy = UiKit.Combo(atcProxyChoices, atcProxyIndex);

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

        var status = UiKit.Status();

        var save = UiKit.Button("Save", () =>
        {
            if (UiKit.TryReadInt(monitor.Text, out var m)) s.MonitorDelay = m;
            if (UiKit.TryReadInt(retry.Text, out var r)) s.RetryDelay = r;
            if (UiKit.TryReadInt(timeout.Text, out var t)) s.Timeout = t;
            languageSvc.Select(language.SelectedItem as string);
            s.Currency = (Core.Models.Currency)Math.Max(0, currency.SelectedIndex);
            s.StartupPage = (StartupPage)Math.Max(0, startup.SelectedIndex);
            s.QueuePresentation = (QueuePresentation)Math.Max(0, queue.SelectedIndex);
            if (UiKit.TryReadInt(clock.Text, out var ck)) s.Clock = ck;
            s.EnableClock = enableClock.IsChecked == true;
            if (!string.IsNullOrWhiteSpace(clockFormat.Text)) s.ClockFormat = clockFormat.Text!;

            // index 0 is the "(task proxy)" placeholder, so index-1 maps into the groups
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
                    services.Config.ProxyGroups.Count - 1)].Id;
            s.MonitorConcurrency.Mode = (ConcurrencyMode)Math.Max(0, concMode.SelectedIndex);
            if (UiKit.TryReadInt(concMax.Text, out var mx)) s.MonitorConcurrency.Maximum = mx;
            if (double.TryParse(concRatio.Text, out var ratio)) s.MonitorConcurrency.Ratio = ratio;

            services.Config.Save();
            status.Text = "Saved.";
        });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                UiKit.Row("(i)  Language", language),
                new TextBlock { Text = "Default Delays", Opacity = 0.6, Margin = new Thickness(0, 6, 0, 0) },
                new Grid
                {
                    ColumnDefinitions = new ColumnDefinitions("*,*,*"),
                    Children =
                    {
                        UiKit.Row("Default Monitor", UiKit.WithUnit(monitor, "ms"), 120),
                        DockedColumn(UiKit.Row("Default Error", UiKit.WithUnit(retry, "ms"), 120), 1),
                        DockedColumn(UiKit.Row("Default Timeout", UiKit.WithUnit(timeout, "sec"), 120), 2),
                    },
                }),
            UiKit.PlainCard(
                new TextBlock { Text = "Quicktask Settings", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },
                UiKit.Row("Default Profiles", quickProfiles),
                UiKit.Row("Default Proxies", quickProxies)),
            UiKit.PlainCard(
                new TextBlock { Text = "Shopify Settings", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },
                UiKit.Row("ATC Browser Proxy", atcProxy),
                UiKit.Row("Queue Presentation", queue)),
            UiKit.PlainCard(
                // R216: measured on the running build — "Monitor Concurrency" is ONE row with an info marker, a mode
                // dropdown and a number box ("[Maximum ▾] [3 max]"), not a three-row section. Ratio is a *mode value*
                // (Settings.General.MonitorConcurrency.Ratio), which is why it never had a row of its own.
                UiKit.Row("(i)  Monitor Concurrency", ConcurrencyRow(concMode, concMax, concRatio))),
            UiKit.PlainCard(
                UiKit.Row("(i)  Startup Page", startup)),
            UiKit.PlainCard(
                UiKit.Row("(i)  Currency", currency)),
            UiKit.PlainCard(
                UiKit.Row("Enable clock", enableClock),
                UiKit.Row("Clock format", clockFormat)),
            UiKit.Buttons(save),
            status));
    }

    /// <summary>The mode dropdown and the two number boxes on one line, as the window draws them.</summary>
    private static Control ConcurrencyRow(Control mode, Control maximum, Control ratio)
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        row.Children.Add(mode);
        // R757: the comment above the call site has said "[3 max]" since R216; the suffix is now drawn.
        row.Children.Add(UiKit.WithUnit(maximum, "max"));
        row.Children.Add(ratio);
        return row;
    }

    /// <summary>Puts a control in a specific column of the row it is added to.</summary>
    private static Control DockedColumn(Control control, int column)
    {
        Grid.SetColumn(control, column);
        return control;
    }
}

/// <summary>
/// Appearance (Cybersole.Ui.Views.Settings.AppearanceView) — the scrollbar knobs and the preview
/// block under them.
///
/// <para>
/// R75 read the live page: <c>Scrollbar Width</c> (px), <c>Corner Radius</c> (px),
/// <c>Scrollbar Color</c>, then a PREVIEW card holding ten caption lines and enough rows to
/// actually scroll. The ten captions are the ones the locale ships, so they are printed verbatim
/// rather than paraphrased — the point of the block is that it scrolls.
/// </para>
/// </summary>
public sealed class AppearanceView : UserControl
{
    /// <summary>The ten preview captions, in the order the live page prints them.</summary>
    public static readonly IReadOnlyList<string> PreviewCaptions = new[]
    {
        "Scroll to test the scrollbar appearance",
        "The scrollbar on the right reflects your current settings",
        "Adjust the width if the scrollbar is too small to grab",
        "Try different colors to match your preference",
        "Corner radius controls how rounded the scrollbar looks",
        "Changes apply immediately across the application",
        "Settings are saved automatically",
        "Use the Reset Defaults button to restore original settings",
        "Scroll down to see more content",
        "This preview area lets you test before leaving settings",
    };

    /// <summary>Restores the scrollbar defaults (bound as <c>ResetDefaults</c>).</summary>
    private void ResetDefaultsCore()
    {
        var s = _appearanceServices?.Config.Settings;
        if (s is null) return;

        s.ScrollbarWidth = 10;
        s.ScrollbarCornerRadius = 6;
        s.ScrollbarColor = "#FFFFFF";
        _appearanceServices!.Config.Save();
    }

    private AppServices? _appearanceServices;

    // R499: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>ResetDefaults</c>; behaviour unchanged (was a method).</summary>
    public ICommand ResetDefaults { get; }

    public AppearanceView(AppServices services)
    {
        ResetDefaults = new RelayCommand(ResetDefaultsCore);

        _appearanceServices = services;
        var s = services.Config.Settings;
        var status = UiKit.Status();

        var width = UiKit.Text(s.ScrollbarWidth.ToString("0.#"), watermark: "10");
        var radius = UiKit.Text(s.ScrollbarCornerRadius.ToString("0.#"), watermark: "6");
        var colour = UiKit.Text(s.ScrollbarColor, watermark: "#FFFFFF");

        var preview = new StackPanel { Spacing = 10 };
        preview.Children.Add(new TextBlock
        {
            Text = "PREVIEW",
            Opacity = 0.6,
            FontSize = 11,
        });
        foreach (var caption in PreviewCaptions)
            preview.Children.Add(new TextBlock { Text = caption, Opacity = 0.75 });

        var save = UiKit.Button("Save", () =>
        {
            if (double.TryParse(width.Text, out var w)) s.ScrollbarWidth = w;
            if (double.TryParse(radius.Text, out var r)) s.ScrollbarCornerRadius = r;
            if (!string.IsNullOrWhiteSpace(colour.Text)) s.ScrollbarColor = colour.Text!;
            services.Config.Save();
            status.Text = "Saved.";
        });

        // R243: the button's work is a named command now — the original binds ResetDefaults on this page
        // (analysis/xaml_bindings.json), and the page's own preview caption promises the button by that name.
        var reset = UiKit.Button("Reset Defaults", () =>
        {
            ResetDefaultsCore();
            services.Config.Save();
            status.Text = "Scrollbar settings reset.";
        });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                new TextBlock { Text = "Scrollbar", Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },
                UiKit.Row("Scrollbar Width", width),
                UiKit.Row("Corner Radius", radius),
                UiKit.Row("Scrollbar Color", colour)),
            UiKit.PlainCard(preview),
            UiKit.Buttons(save, reset),
            status));
    }
}

/// <summary>
/// Notifications (Cybersole.Ui.Views.Settings.NotificationsView).
///
/// <para>
/// R78 drove all five tabs of the live page. Every one of them is the same panel with a different
/// first line — it is a formula, not five hand-built pages:
/// </para>
///
/// <code>
/// Enable Notifications                        [switch]     page level
/// Checkout | Decline | Captcha | Smart Actions | Other      tab bar
///   Allow {Tab} Notifications                 [switch]
///   In-Bot Notifications                      [switch]
///   Desktop Notifications                     [switch]
///   Sounds                                    [switch]
///   [ Default ]                                            sound file button
///   [ Reset ]  [ Play ]
/// </code>
///
/// <para>
/// The five first lines read <c>Allow Checkout Notifications</c>, <c>Allow Decline Notifications</c>,
/// <c>Allow Captcha Notifications</c>, <c>Allow Smart Actions Notifications</c> and
/// <c>Allow Other Notifications</c> — the tab name and the word "Notifications", nothing else.
/// </para>
///
/// <para>
/// The tab bar is five text buttons, not a <see cref="TabControl"/>: the live page underlines
/// nothing and boxes nothing, it just makes the active word white and bold.
/// </para>
/// </summary>
public sealed class NotificationsView : UserControl
{
    /// <summary>The five categories, in the order the live page lists them.</summary>
    public static readonly IReadOnlyList<string> Tabs = new[]
    {
        "Checkout", "Decline", "Captcha", "Smart Actions", "Other",
    };

    /// <summary>The notification categories (bound as <c>Types</c>) — the same five the tabs carry.</summary>
    public static IReadOnlyList<string> Types => Tabs;

    /// <summary>What the first switch on each tab says: "Allow " + tab + " Notifications".</summary>
    public static string AllowLabel(string tab) => "Allow " + tab + " Notifications";

    /// <summary>The options object behind a tab.</summary>
    public static NotificationOptions OptionsFor(GlobalSettings settings, string tab) => tab switch
    {
        "Checkout" => settings.NotificationOptions.Checkout,
        "Decline" => settings.NotificationOptions.Decline,
        "Captcha" => settings.NotificationOptions.Captcha,
        "Smart Actions" => settings.NotificationOptions.SmartAction,
        _ => settings.NotificationOptions.Other,
    };

    // ------------------------------------------------ bound commands (R239)
    //
    // The original binds SelectSound / ResetSound on NotificationsView (analysis/xaml_bindings.json).
    // The "Default / <file>" button and the "Reset" button below did this inline; the names are what a rebinding
    // addresses, so the work sits in methods and the buttons call them.

    private AppServices? _services;

    /// <summary>The sound path for a tab; empty means the platform default (bound as <c>SelectSound</c>).</summary>
    public string SelectSound(string tab, string path)
    {
        var options = OptionsFor(_services!.Config.Settings, tab);
        options.Path = path ?? string.Empty;
        _services.Config.Save();
        return options.Path;
    }

    /// <summary>Puts a tab back on the default sound (bound as <c>ResetSound</c>).</summary>
    public void ResetSound(string tab) => SelectSound(tab, string.Empty);

    public NotificationsView(AppServices services)
    {
        _services = services;
        var s = services.Config.Settings;
        var status = UiKit.Status();

        // ---- page-level master switch
        var master = UiKit.Switch("Enable Notifications", s.Notifications, on =>
        {
            s.Notifications = on;
            services.Config.Save();
            status.Text = on ? "Notifications enabled." : "Notifications disabled.";
        });

        // ---- tab bar
        var bar = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 18 };
        var tabButtons = new Dictionary<string, Button>(StringComparer.Ordinal);
        var host = new ContentControl();

        void Select(string tab)
        {
            foreach (var (name, button) in tabButtons)
            {
                var active = name == tab;
                button.FontWeight = active ? FontWeight.SemiBold : FontWeight.Normal;
                button.Foreground = active ? Brushes.White : UiKit.Dim;
            }

            host.Content = BuildPanel(tab, services, status);
        }

        foreach (var tab in Tabs)
        {
            var name = tab;
            var button = new Button
            {
                Content = tab,
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(2, 4),
                FontSize = 14,
            };
            button.Click += (_, _) => Select(name);
            tabButtons[tab] = button;
            bar.Children.Add(button);
        }

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(master),
            UiKit.PlainCard(bar, host),
            status));

        Select("Checkout");
    }

    /// <summary>
    /// One tab's panel. Identical for all five except the first caption, which is the whole point
    /// of building it here instead of five times.
    /// </summary>
    private static Control BuildPanel(string tab, AppServices services, TextBlock status)
    {
        var s = services.Config.Settings;
        var options = OptionsFor(s, tab);

        // Every one of these is a switch on the live page, not a checkbox.
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
        });

        // ---- the sound file button. "Default" is an empty path, which the player turns into the
        // platform's notification sound; a chosen file is played as-is.
        var picker = new Button
        {
            Content = string.IsNullOrWhiteSpace(options.Path)
                ? "Default"
                : System.IO.Path.GetFileName(options.Path),
            HorizontalContentAlignment = HorizontalAlignment.Left,
            HorizontalAlignment = HorizontalAlignment.Stretch,
            Padding = new Thickness(12, 8),
        };
        ToolTip.SetTip(picker, string.IsNullOrWhiteSpace(options.Path)
            ? "The default notification sound. Click to choose a .wav file."
            : options.Path);

        picker.Click += async (_, _) =>
        {
            if (TopLevel.GetTopLevel(picker)?.StorageProvider is not { CanOpen: true } sp)
            {
                status.Text = "This platform has no file dialog.";
                return;
            }

            var files = await sp.OpenFilePickerAsync(new Avalonia.Platform.Storage.FilePickerOpenOptions
            {
                Title = "Choose a notification sound",
                AllowMultiple = false,
                FileTypeFilter = new[]
                {
                    new Avalonia.Platform.Storage.FilePickerFileType("Sound files")
                    {
                        Patterns = new[] { "*.wav", "*.mp3" },
                    },
                },
            }).ConfigureAwait(true);

            var file = files.FirstOrDefault();
            if (file is null) return;

            options.Path = file.Path.LocalPath;
            services.Config.Save();
            picker.Content = System.IO.Path.GetFileName(options.Path);
            ToolTip.SetTip(picker, options.Path);
            status.Text = $"{tab} sound is now {picker.Content}.";
        };

        var reset = UiKit.Button("Reset", () =>
        {
            options.Path = string.Empty;
            services.Config.Save();
            picker.Content = "Default";
            ToolTip.SetTip(picker, "The default notification sound. Click to choose a .wav file.");
            status.Text = $"{tab} sound reset to the default.";
        });

        // Play goes through the same player the fan-out uses, so the button proves the real path.
        var play = UiKit.Button("Play", () =>
        {
            services.Notify.PlaySound(options.Path);
            status.Text = string.IsNullOrWhiteSpace(options.Path)
                ? $"Playing the default sound for {tab}."
                : $"Playing {System.IO.Path.GetFileName(options.Path)}.";
        });

        return new StackPanel
        {
            Spacing = 10,
            Children =
            {
                allow,
                centre,
                desktop,
                sound,
                picker,
                UiKit.Buttons(reset, play),
            },
        };
    }
}

/// <summary>
/// Keyboard Shortcuts (Cybersole.Ui.Views.Settings.KeyBindsView).
///
/// <para>
/// R76 drove the live page and copied the whole table. Three sections — Tasks, Proxies and Billing —
/// each listing two bindings per row, each with its chord in a chip and an ✕ to clear it, under a
/// single <c>Enable Keyboard Shortcuts</c> switch:
/// </para>
///
/// <code>
/// Tasks    New Group Ctrl+G      Task Creator Ctrl+N
///          Task Editor Ctrl+E    Start All F1
///          Stop All F2           Delete Selected Delete
///          Clone Selected Ctrl+C Search Ctrl+F
///          Quicktask Ctrl+Q      Link Change Ctrl+M
///          Next Group Ctrl+Right Previous Group Ctrl+Left
/// Proxies  New Group Ctrl+G      Add Proxies Ctrl+N
///          Test All Ctrl+T       Copy Selected Ctrl+C
///          Clone Selected Ctrl+D Delete Selected Delete
/// Billing  New Group Ctrl+G      Add Profile Ctrl+N
///          Clone Selected Ctrl+D Delete Selected Delete
/// </code>
///
/// <para>
/// The model already carried all 22 (<see cref="TaskKeyBinds"/> 12, <see cref="ProxyKeyBinds"/> 6,
/// <see cref="BillingKeyBinds"/> 4) — R116 read them off this same page. The <b>view</b> listed
/// seven, four and three, with invented labels, so five task chords had no row at all and the clash
/// check could not see them.
/// </para>
/// </summary>
public sealed class KeyBindsView : UserControl
{
    /// <summary>The Tasks chords, in the live page's order, with the labels it prints.</summary>
    public static readonly IReadOnlyList<string> TaskLabels = new[]
    {
        "New Group", "Task Creator", "Task Editor", "Start All", "Stop All", "Delete Selected",
        "Clone Selected", "Search", "Quicktask", "Link Change", "Next Group", "Previous Group",
    };

    /// <summary>The Proxies chords, in order.</summary>
    public static readonly IReadOnlyList<string> ProxyLabels = new[]
    {
        "New Group", "Add Proxies", "Test All", "Copy Selected", "Clone Selected", "Delete Selected",
    };

    /// <summary>The Billing chords, in order.</summary>
    public static readonly IReadOnlyList<string> BillingLabels = new[]
    {
        "New Group", "Add Profile", "Clone Selected", "Delete Selected",
    };

    public KeyBindsView(AppServices services)
    {
        var s = services.Config.Settings;
        var status = UiKit.Status();

        // the row currently listening for a chord, if any
        (Button Button, KeyBind Bind, string Page, string Label)? capturing = null;

        // every editable chord and the button that displays it, so capture can repaint its own row
        var pairs = new List<(KeyBind Bind, Button Button)>();

        void EndCapture(string? message)
        {
            if (capturing is not { } c) return;
            c.Button.Content = Cybersole.Core.Input.KeyBindMatcher.Describe(c.Bind);
            capturing = null;
            if (message is not null) status.Text = message;
        }

        Control Section(string title, string page, params (string Label, KeyBind Bind)[] binds)
        {
            // Six columns: label, chip, X for the left pair, then the same three for the right
            // pair. R76: with five, the right-hand X had no column to land in and drew on
            // top of its own chip ("×Ctrl+N").
            var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("150,Auto,24,150,Auto,24") };

            for (var i = 0; i < binds.Length; i++)
            {
                var row = i / 2;
                var right = i % 2 == 1;
                var first = right ? 3 : 0;

                while (grid.RowDefinitions.Count <= row)
                    grid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));

                var (label, bind) = binds[i];

                var text = new TextBlock
                {
                    Text = label,
                    VerticalAlignment = VerticalAlignment.Center,
                    Margin = new Thickness(0, 3, 8, 3),
                };
                Grid.SetRow(text, row);
                Grid.SetColumn(text, first);
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
                Grid.SetColumn(capture, first + 1);
                grid.Children.Add(capture);
                pairs.Add((bind, capture));

                // The X clears the chord; Key 0 matches nothing, which is the unbound state.
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
                Grid.SetColumn(clear, first + 2);
                grid.Children.Add(clear);
            }

            return UiKit.PlainCard(
                new TextBlock { Text = title, Opacity = 0.6, Margin = new Thickness(0, 0, 0, 6) },
                grid);
        }

        var tasks = Section("Tasks", "Tasks",
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

        // One handler on the page, not one per row: the capture target changes and a page-level
        // tunnel sees the key before any child control consumes it.
        AddHandler(KeyDownEvent, (_, e) =>
        {
            if (capturing is not { } c) return;

            e.Handled = true;

            if (e.Key == Avalonia.Input.Key.Escape)
            {
                EndCapture("Capture cancelled.");
                return;
            }

            var code = Cybersole.Core.Input.KeyBindMatcher.VirtualKey(e.Key.ToString());
            if (code == 0)
            {
                status.Text = $"{e.Key} cannot be used as a shortcut.";
                return;
            }

            var mods = Cybersole.Core.Input.KeyBindMatcher.Modifiers(
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Alt),
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Control),
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Shift));

            // A chord that already exists on the same page would make one of the two unreachable,
            // because the handler matches in declaration order.
            var clash = AllOnPage(s, c.Page)
                .FirstOrDefault(o => o.Bind != c.Bind
                                     && o.Bind.Key == code
                                     && o.Bind.Modifiers == mods);

            if (clash.Bind is not null)
            {
                status.Text = $"{Cybersole.Core.Input.KeyBindMatcher.Describe(clash.Bind)} is already "
                            + $"{clash.Label} on this page.";
                return;
            }

            c.Bind.Key = code;
            c.Bind.Modifiers = mods;
            services.Config.Save();

            var described = Cybersole.Core.Input.KeyBindMatcher.Describe(c.Bind);
            EndCapture($"{c.Page} · {c.Label} is now {described}.");
        }, Avalonia.Interactivity.RoutingStrategies.Tunnel);

        // The original's whole page-level control is one switch. The replica had four buttons here
        // (Enable / Disable / Reset / Save); the switch covers the first two, and every edit saves
        // immediately, which is what the X and the capture already do.
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
    }

    /// <summary>
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
}

/// Email accounts (Cybersole.Ui.Views.Settings.ImapView). Manages IMAP rows plus the AYCD
/// inbox block — both backed by the services added in R4.
/// </summary>
public sealed class ImapView : UserControl
{
    /// <summary>Bound as <c>Add</c>: the same command the "Add Accounts" button carries.</summary>
    public ICommand Add { get; }

    /// <summary>Bound as <c>Clear</c>: the same command the "Clear Accounts" button carries.</summary>
    public ICommand Clear { get; }

    /// <summary>Bound as <c>Delete</c>: the same command the "Delete Selected" button carries.</summary>
    public ICommand Delete { get; }


    /// <summary>The live page's three columns, read off the running build in R75.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Host", "Email", "Inbox Count" };

    /// <summary>The empty state's second line, as the live page words it.</summary>
    public const string EmptySubtitle = "Add some accounts to get started";

    /// <summary>The six Imap Provider presets the live Add Imap Account dialog offers.</summary>
    public static readonly IReadOnlyList<string> ImapHosts = new[]
    {
        "imap.gmail.com", "imap.mail.yahoo.com", "imap.mail.me.com",
        "imap.qq.com", "imap.163.com", "outlook.office365.com",
    };

    // ------------------------------------------------ bound commands (R245)
    //
    // The original binds DisconnectAycd on ImapView (analysis/xaml_bindings.json): the page shows the AYCD inbox
    // connection state, so it also needs the way to drop it.

    private AppServices? _imapServices;
    private TextBlock? _imapStatus;

    /// <summary>
    /// Turns the AYCD inbox connection on (bound as <c>Configure</c>).
    ///
    /// <para>
    /// Evidence: the original's ImapView command table is <c>Configure</c> / <c>DisconnectAycd</c>
    /// (<c>analysis/pe_strings.txt</c> 0x0351def6), with a second copy beside
    /// <c>&lt;ExecuteConfigure&gt;d__23</c> and <c>&lt;get_Refresh&gt;b__14_0</c> (0x0351e090) — i.e.
    /// the command's body is an async state machine, and the page also refreshes. The replica has
    /// Connect / Disconnect / Refresh already: Configure is the same action under the original's name.
    /// </para>
    /// </summary>
    public ICommand Configure { get; }

    /// <summary>The <c>Configure</c> body: what the Connect button does. Returns the sentence to print.</summary>
    public string ConfigureAycd()
    {
        var doc = _imapServices?.Config.Accounts;
        if (doc is null) return "No account document.";

        var aycd = doc.AycdInbox;
        if (string.IsNullOrEmpty(aycd.ApiKey)) return "Add an AYCD API key first.";

        aycd.Enabled = true;
        _imapServices!.Config.Save();

        return "AYCD Inbox enabled. Verifying connection...";
    }

    public async Task<string> VerifyAycdAsync(string? origin = null, CancellationToken ct = default)
    {
        var services = _imapServices;
        var aycd = services?.Config.Accounts.AycdInbox;
        if (services is null || aycd is null) return "No account document.";
        if (string.IsNullOrWhiteSpace(aycd.ApiKey)) return "Add an AYCD API key first.";

        var (ok, error, credits) = await services.Mail.VerifyAycdAsync(aycd.ApiKey, origin, ct).ConfigureAwait(false);
        if (!ok)
        {
            aycd.Enabled = false;
            services.Config.Save();
            return $"AYCD verify failed: {error}";
        }

        aycd.Enabled = true;
        services.Config.Save();
        return credits.HasValue
            ? $"AYCD Inbox connected ({credits.Value} credits)."
            : "AYCD Inbox connected.";
    }

    public async Task<string> VerifyImapAccountAsync(ImapAccount account, CancellationToken ct = default)
    {
        var services = _imapServices;
        if (services is null) return "No account document.";
        var (ok, count, error) = await services.Mail.VerifyImapAsync(account, ct).ConfigureAwait(false);
        if (!ok) return $"IMAP verify failed ({account.User}): {error}";
        account.InboxCount = count;
        services.Config.Save();
        return $"IMAP connected ({account.User}: {count} messages).";
    }

    /// <summary>
    /// Drops the AYCD inbox connection: clears the API key and switches the inbox off (bound as <c>DisconnectAycd</c>).
    /// Returns false when there was nothing connected.
    /// </summary>
    // ------------------------------------------------ copy from the image's locale (R401)

    /// <summary>"Connect" — the AYCD connect button (Settings.Aycd.ConnectButton).</summary>
    public const string AycdConnectLabel = "Connect";

    /// <summary>"Disconnect" — the AYCD disconnect action (Settings.Aycd.Disconnect.Action).</summary>
    public const string AycdDisconnectLabel = "Disconnect";

    private bool DisconnectAycdCore()
    {
        var doc = _imapServices?.Config.Accounts;
        if (doc is null) return false;

        var aycd = doc.AycdInbox;
        if (string.IsNullOrEmpty(aycd.ApiKey) && !aycd.Enabled) return false;

        aycd.ApiKey = string.Empty;
        aycd.Enabled = false;
        _imapServices!.Config.Save();
        return true;
    }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>DisconnectAycd</c>; behaviour unchanged (was a method).</summary>
    public ICommand DisconnectAycd { get; }

    public ImapView(AppServices services)
    {
        DisconnectAycd = new RelayCommand(() => DisconnectAycdCore());

        _imapServices = services;
        Configure = new RelayCommand(() => { if (_imapStatus is not null) _imapStatus.Text = ConfigureAycd(); });
        var doc = services.Config.Accounts;
        var status = UiKit.Status();
        _imapStatus = status;
        // R84: a table, not a list of formatted strings — the live page has three columns.
        var rows = new AccountTable(Columns, EmptyView.Headline, EmptySubtitle);
        var count = new TextBlock { Opacity = 0.7 };

        var aycd = doc.AycdInbox;
        var aycdDot = new TextBlock { Text = "●", Foreground = Brushes.IndianRed };
        var aycdState = new TextBlock { Text = "Not connected", Opacity = 0.7 };

        void Refresh()
        {
            rows.Rows = doc.Imap
                .Select(a => new[] { a.Host, a.User, a.InboxCount.ToString() })
                .ToArray();

            count.Text = doc.Imap.Count + (doc.Imap.Count == 1 ? " Account" : " Accounts");

            var connected = aycd.Enabled && !string.IsNullOrEmpty(aycd.ApiKey);
            aycdDot.Foreground = connected ? Brushes.MediumSeaGreen : Brushes.IndianRed;
            aycdState.Text = connected ? "Connected" : "Not connected";
        }

        Refresh();

        // Three fields, matching the live dialog. The provider box accepts a free-typed host
        // as well as the presets, which is why it is a TextBox with a suggestion list rather
        // than a plain ComboBox.
        var provider = UiKit.Text(watermark: "Select or enter host");
        var email = UiKit.Text(watermark: "Enter email address");
        var password = UiKit.Text(password: true, watermark: "Enter password");

        void Save()
        {
            var h = provider.Text?.Trim();
            var u = email.Text?.Trim();

            if (string.IsNullOrEmpty(h) || string.IsNullOrEmpty(u))
            {
                status.Text = "Imap provider and email address are required.";
                return;
            }

            doc.Imap.Add(new ImapAccount
            {
                Host = h!,
                Port = 993,
                User = u!,
                Password = password.Text ?? string.Empty,
                UseSsl = true,
            });

            services.Config.Save();
            provider.Text = string.Empty;
            email.Text = string.Empty;
            password.Text = string.Empty;
            Refresh();
            status.Text = "Imap account saved.";
        }

        var connect = UiKit.Button(AycdConnectLabel, async () =>
        {
            status.Text = ConfigureAycd();
            Refresh();
            if (!string.IsNullOrWhiteSpace(aycd.ApiKey))
            {
                status.Text = await VerifyAycdAsync();
                Refresh();
            }
        });

        var testImapButton = UiKit.Button("Test Selected", async () =>
        {
            if (rows.SelectedIndex < 0 || rows.SelectedIndex >= doc.Imap.Count)
            {
                status.Text = "Select an account first.";
                return;
            }
            status.Text = "Connecting...";
            status.Text = await VerifyImapAccountAsync(doc.Imap[rows.SelectedIndex]);
            Refresh();
        });

                var addButton = UiKit.Button("Add Accounts", () =>
                        {
                            provider.Focus();
                            status.Text = "Enter the host, email and password below, then Save.";
                        });
        Add = addButton.Command!;
        var clearButton = UiKit.Button("Clear Accounts", () =>
                        {
                            doc.Imap.Clear();
                            services.Config.Save();
                            Refresh();
                            status.Text = "All accounts cleared.";
                        });
        Clear = clearButton.Command!;
        var deleteButton = UiKit.Button("Delete Selected", () =>
                    {
                        if (rows.SelectedIndex < 0) { status.Text = "Select an account first."; return; }
                        doc.Imap.RemoveAt(rows.SelectedIndex);
                        services.Config.Save();
                        Refresh();
                        status.Text = "Account deleted.";
                    });
        Delete = deleteButton.Command!;

Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("Email Accounts",
                UiKit.Row("Add imap email accounts to automatically login to certain sites",
                    UiKit.Buttons(
                        // "Add Accounts" used to write "Fill in the provider, email address and
                        // password, then Save." and nothing else — advice, not an action. It now
                        // puts the caret where the advice says to start.
                        addButton,
                        clearButton)),
                count,
                rows,
                UiKit.Row("Imap Provider", UiKit.Buttons(provider,
                    UiKit.Combo(ImapHosts))),
                UiKit.Row("Email Address", email),
                UiKit.Row("Password", password),
                UiKit.Row("", UiKit.Buttons(
                    UiKit.Button("Save", Save),
                    testImapButton,
                    deleteButton)),
                new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 8) },
                UiKit.Row("AYCD Inbox", UiKit.Buttons(aycdDot, aycdState, connect)),
                UiKit.Row("AYCD API key", UiKit.Text(aycd.ApiKey, watermark: "AYCD API key"))),
            status));
    }
}

/// <summary>Google accounts (Cybersole.Ui.Views.Settings.GoogleAccountsView).</summary>
public sealed class GoogleAccountsView : UserControl
{
    /// <summary>Bound as <c>Add</c>: the same command the "Add Account" button carries.</summary>
    public ICommand Add { get; }

    /// <summary>Bound as <c>Clear</c>: the same command the "Clear Accounts" button carries.</summary>
    public ICommand Clear { get; }

    /// <summary>Bound as <c>Delete</c>: the same command the "Delete Selected" button carries.</summary>
    public ICommand Delete { get; }


    /// <summary>The live page's two columns (locale: Settings.Google.Header.Name / .Email).</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name", "Email" };

    /// <summary>The empty state's second line, as the live page words it.</summary>
    public const string EmptySubtitle = "Add some Google accounts to get started";

    /// <summary>
    /// The YouTube channel/tab this view is pointed at (bound as <c>YouTube</c>, R366). The image exposes it as a
    /// get/set property and formats a window title as "YouTube - {0}"; what fills it is still unknown, so it is a plain
    /// string with no behaviour behind it.
    /// </summary>
    public string? YouTube { get; set; }

    private readonly AppServices? _googleServices;
    private AccountTable? _googleRows;
    private TextBox? _googleName;
    private TextBox? _googleProxy;
    private TextBlock? _googleStatus;

    /// <summary>
    /// Loads the selected account into the name / proxy fields for editing (bound as <c>Edit</c>).
    ///
    /// <para>
    /// Evidence: the original's GoogleAccountsView command table is
    /// <c>Delete</c> / <c>YouTube</c> / <c>Add</c> / <c>Edit</c> / <c>Clear</c>
    /// (<c>analysis/pe_strings.txt</c> 0x0351ddd2). The replica has Add / Add Manually / Clear /
    /// Delete, so <c>Edit</c> is the one member the command table names and the page lacks. What it
    /// edits is the part the table does not say; the two editable fields the page owns are the same
    /// two the add path fills (display name, bound proxy), so Edit loads those and leaves the save to
    /// the existing add/clear paths.
    /// </para>
    /// </summary>
    public ICommand Edit { get; }

    /// <summary>The <c>Edit</c> body: copies the selected account's editable fields into the form.</summary>
    public string EditSelected()
    {
        var doc = _googleServices?.Config.Accounts;
        var index = _googleRows?.SelectedIndex ?? -1;
        if (doc is null || index < 0 || index >= doc.Google.Count)
        {
            _googleName?.Focus();
            return "Select an account, or add one below.";
        }

        var picked = doc.Google[index];
        if (_googleName is not null) _googleName.Text = picked.Name ?? picked.Email;
        if (_googleProxy is not null) _googleProxy.Text = picked.Proxy;
        _googleName?.Focus();
        return $"Editing {picked.Email}. Change the fields, then Add Manually.";
    }

    public GoogleAccountsView(AppServices services)
    {
        _googleServices = services;
        Edit = new RelayCommand(() => { if (_googleStatus is not null) _googleStatus.Text = EditSelected(); });
        var doc = services.Config.Accounts;
        var status = UiKit.Status();
        // R84: two columns, as the live page shows (Settings.Google.Header.*).
        var rows = new AccountTable(Columns, EmptyView.Headline, EmptySubtitle);
        var count = new TextBlock { Opacity = 0.7 };

        void Refresh()
        {
            rows.Rows = doc.Google
                .Select(g => new[] { g.Name ?? g.Email, g.Email })
                .ToArray();

            count.Text = doc.Google.Count + (doc.Google.Count == 1 ? " Account" : " Accounts");
        }

        Refresh();

        // After OAuth lands, the user still supplies the display name and the proxy to bind.
        var name = UiKit.Text(watermark: "Display name");
        var proxy = UiKit.Text(watermark: "host:port:user:pass");
        var manualEmail = UiKit.Text(watermark: "name@gmail.com");

        // R432: the bound Edit command reads/writes these, so keep the handles.
        _googleRows = rows;
        _googleName = name;
        _googleProxy = proxy;
        _googleStatus = status;

        // Real sign-in: launch Chrome, walk the Google login, read the identity back.
        async void AddViaSignIn()
        {
            status.Text = "Opening the Google sign-in page...";

            try
            {
                await using var flow = await Cybersole.Stores.Accounts.GoogleOAuthFlow
                    .BeginAsync(null, CancellationToken.None).ConfigureAwait(true);

                status.Text = "Waiting for sign-in to finish (5 minutes)...";

                var result = await flow.CompleteAsync(TimeSpan.FromMinutes(5),
                    CancellationToken.None).ConfigureAwait(true);

                if (!result.Success || result.Account is null)
                {
                    status.Text = result.Error ?? "Sign-in failed.";
                    return;
                }

                result.Account.Name = string.IsNullOrWhiteSpace(name.Text)
                    ? result.Account.Name
                    : name.Text;
                result.Account.Proxy = proxy.Text;

                doc.Google.Add(result.Account);
                services.Config.Save();
                Refresh();
                status.Text = "Linked " + result.Account.Email + ".";
            }
            catch (Exception ex)
            {
                status.Text = "Sign-in failed: " + ex.Message;
            }
        }

                var addButton = UiKit.Button("Add Account", AddViaSignIn);
        Add = addButton.Command!;
        var clearButton = UiKit.Button("Clear Accounts", () =>
                        {
                            doc.Google.Clear();
                            services.Config.Save();
                            Refresh();
                            status.Text = "All accounts cleared.";
                        });
        Clear = clearButton.Command!;
        var deleteButton = UiKit.Button("Delete Selected", () =>
                {
                    if (rows.SelectedIndex < 0) { status.Text = "Select an account first."; return; }
                    doc.Google.RemoveAt(rows.SelectedIndex);
                    services.Config.Save();
                    Refresh();
                    status.Text = "Deleted.";
                });
        Delete = deleteButton.Command!;

Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("Google Accounts",
                UiKit.Row("Store Google accounts for easy access when using solvers",
                    UiKit.Buttons(
                        addButton,
                        clearButton)),
                count,
                rows,
                UiKit.Row("Name", name),
                UiKit.Row("Proxy", proxy),
                new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 8) },
                UiKit.Row("Or add without signing in", UiKit.Buttons(manualEmail,
                    UiKit.Button("Add Manually", () =>
                    {
                        if (string.IsNullOrWhiteSpace(manualEmail.Text))
                        {
                            status.Text = "Email required.";
                            return;
                        }

                        doc.Google.Add(new GoogleAccount
                        {
                            Email = manualEmail.Text!,
                            Name = string.IsNullOrWhiteSpace(name.Text)
                                ? manualEmail.Text!.Split('@')[0]
                                : name.Text,
                            Proxy = proxy.Text,
                            State = "Manual",
                        });

                        services.Config.Save();
                        manualEmail.Text = string.Empty;
                        Refresh();
                        status.Text = "Added without a sign-in.";
                    }))),
                UiKit.Row("", deleteButton)),
            status));
    }
}

/// <summary>PayPal accounts (Cybersole.Ui.Views.Settings.PayPalAccountsView).</summary>
public sealed class PayPalAccountsView : UserControl
{
    /// <summary>The live page's two columns (locale: Settings.PayPal.Header.Email / .Status).</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Email", "Status" };

    /// <summary>The empty state's second line, as the live page words it.</summary>
    public const string EmptySubtitle = "Add some PayPal accounts to get started";

    /// <summary>
    /// R481: the original binds <c>Add</c> / <c>Clear</c> as **properties** on this view. Both actions already
    /// existed as button lambdas that close over the local inputs, so they stay lambdas — only their exposure
    /// changes.
    /// </summary>
    public ICommand Add { get; }

    /// <inheritdoc cref="Add"/>
    public ICommand Clear { get; }

    /// <summary>Bound as <c>Edit</c>; acts on the selected row (was an unnamed button lambda).</summary>
    public ICommand Edit { get; }

    /// <summary>Bound as <c>Toggle</c>; acts on the selected row (was an unnamed button lambda).</summary>
    public ICommand Toggle { get; }

    /// <summary>Bound as <c>Delete</c>; acts on the selected row (was an unnamed button lambda).</summary>
    public ICommand Delete { get; }


    public PayPalAccountsView(AppServices services)
    {
        var doc = services.Config.Accounts;
        var status = UiKit.Status();
        // R84: two columns, as the live page shows (Settings.PayPal.Header.*).
        var rows = new AccountTable(Columns, EmptyView.Headline, EmptySubtitle);

        void Refresh() => rows.Rows = doc.PayPal
            .Select(p => new[] { p.Email, p.Running ? "Active" : "Inactive" })
            .ToArray();

        Refresh();

        var email = UiKit.Text(watermark: "paypal email");
        var password = UiKit.Text(password: true);
        var proxyGroup = UiKit.Text(watermark: "proxy group");
        var useLoginProxy = UiKit.Check("Use login proxy", true);
        var autoReopen = UiKit.Check("Auto reopen", false);
        var inactiveAfter = UiKit.Number(0);

            Add = new RelayCommand(() =>
            {
                if (string.IsNullOrWhiteSpace(email.Text)) { status.Text = "Email required."; return; }
                doc.PayPal.Add(new PayPalAccount
                {
                    Email = email.Text!,
                    ProxyGroup = proxyGroup.Text,
                    Running = false,
                });
                services.Config.Save();
                Refresh();
                status.Text = "Added.";
            });
        Edit = new RelayCommand(() => {
                        if (rows.SelectedIndex < 0) return;
                        var p = doc.PayPal[rows.SelectedIndex];
                        p.Email = email.Text ?? p.Email;
                        p.ProxyGroup = proxyGroup.Text;
                        services.Config.Save();
                        Refresh();
                        status.Text = "Updated.";
                    });
        Toggle = new RelayCommand(() => {
                        if (rows.SelectedIndex < 0) return;
                        var p = doc.PayPal[rows.SelectedIndex];
                        p.Running = !p.Running;
                        p.LastRefresh = DateTime.UtcNow;
                        services.Config.Save();
                        Refresh();
                        status.Text = $"Running = {p.Running}.";
                    });
        Delete = new RelayCommand(() => {
                        if (rows.SelectedIndex < 0) return;
                        doc.PayPal.RemoveAt(rows.SelectedIndex);
                        services.Config.Save();
                        Refresh();
                        status.Text = "Deleted.";
                    });

            Clear = new RelayCommand(() =>
            {
                doc.PayPal.Clear();
                services.Config.Save();
                Refresh();
                status.Text = "Cleared.";
            });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("PayPal accounts",
                rows,
                UiKit.Row("Email", email),
                UiKit.Row("Password", password),
                UiKit.Row("Proxy group", proxyGroup),
                UiKit.Row("Login proxy", useLoginProxy),
                UiKit.Row("Auto reopen", autoReopen),
                UiKit.Row("Inactivate after (min)", inactiveAfter),

                UiKit.Buttons(
                    UiKit.Button("Add", () => Add.Execute(null)),
                    UiKit.Button("Edit", () => Edit.Execute(null)),
                    UiKit.Button("Delete", () => Delete.Execute(null)),
                    UiKit.Button("Toggle", () => Toggle.Execute(null)),
                    UiKit.Button("Clear", () => Clear.Execute(null)))),
            status));
    }
}

/// <summary>Payment / 3-D Secure settings (Cybersole.Ui.Views.Settings.PaymentView).</summary>
public sealed class PaymentView : UserControl
{
    /// <summary>Bound as <c>Refresh</c>; the button with that label runs this command.</summary>
    public ICommand Refresh { get; }


    /// <summary>
    /// The controls the live page shows at rest, in its order, read off the running build in R77.
    ///
    /// <para>
    /// Six of them, in three sections:
    /// </para>
    ///
    /// <code>
    /// 3D Secure         Auto Open 3DS                     [No]
    /// External Browser  Browser Path                      [None] [Configure]
    ///                   Maximum Browser Tabs              [10]
    ///                   Open Link As                      [Tab]
    /// Browser Profiles  Checkout Profiles                 [Browser default] [Refresh]
    ///                   Profile Assignment                [Round robin]
    /// </code>
    ///
    /// <para>
    /// The locale carries a seventh field — <c>Settings.Payment.AutoOpen3DSLimit</c>, "Max Open" —
    /// which the replica renders and the live page does not show at rest. Whether it is conditional
    /// on Auto Open 3DS or simply has no control is <b>unresolved</b>: the live build's combo boxes
    /// expose no accessibility peer and a click does not open their popup, so the value could not be
    /// switched to find out.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> LiveControls = new[]
    {
        "Auto Open 3DS",
        "Browser Path",
        "Maximum Browser Tabs",
        "Open Link As",
        "Checkout Profiles",
        "Profile Assignment",
    };

    /// <summary>
    /// The Profile Assignment choices as the live page prints them. The enum calls the first one
    /// <c>RoundRobin</c>; the page calls it "Round robin", and the space is the difference between
    /// a UI and a debug view.
    /// </summary>
    public static readonly IReadOnlyList<string> AssignmentChoices = new[]
    {
        "Round robin", "Random", "Least used",
    };

    /// <summary>The three section headings, in the live page's order.</summary>
    public static readonly IReadOnlyList<string> LiveSections = new[]
    {
        "3D Secure", "External Browser", "Browser Profiles",
    };


    // ------------------------------------------------ bound members (R238)
    //
    // The original binds DetectedProfiles / SelectedProfiles on PaymentView (analysis/xaml_bindings.json).
    // Detected is what BrowserProfileScanner found and stored; Selected is what the Checkout Profiles combo holds.

    private ComboBox? _checkoutProfile;
    private readonly AppServices _services;

    // the field is assigned in the constructor below

    /// <summary>The browser profiles detected on this machine (bound as <c>DetectedProfiles</c>).</summary>
    public IReadOnlyList<string> DetectedProfiles => _services.Config.Settings.BrowserProfiles;

    /// <summary>The checkout profile currently chosen (bound as <c>SelectedProfiles</c>).</summary>
    public IReadOnlyList<string> SelectedProfiles
    {
        get
        {
            var choice = _checkoutProfile?.SelectedItem as string;
            return string.IsNullOrWhiteSpace(choice) ? Array.Empty<string>() : new[] { choice };
        }
    }

    /// <summary>Re-scans the machine for browser profiles (what the Refresh button does).</summary>
    public IReadOnlyList<string> RescanProfiles()
    {
        var found = Cybersole.Services.BrowserProfileScanner.Scan();
        if (found.Count == 0) return found;

        _services.Config.Settings.BrowserProfiles = found;
        _services.Config.Save();
        return found;
    }

    /// <summary>Bound as <c>Configure</c>: the same command instance the "Configure" button carries.</summary>
    public ICommand Configure { get; }

    public PaymentView(AppServices services)
    {
        _services = services;
        var s = services.Config.Settings;
        var status = UiKit.Status();

        // Layout mirrors the live 5.18.32 Payment page (docs/GUI_BASELINE.md).
        var auto3ds = UiKit.Combo(new[] { "No", "Yes" }, s.AutoOpen3DS ? 1 : 0);
        var auto3dsLimit = UiKit.Number(s.AutoOpen3DSLimit);

        // R330: measured on the running build — "Max Open" only exists while "Auto Open 3DS" is Yes.
        var maxOpen = UiKit.Row("Max Open", auto3dsLimit);
        maxOpen.IsVisible = s.AutoOpen3DS;
        auto3ds.SelectionChanged += (_, _) => maxOpen.IsVisible = auto3ds.SelectedIndex == 1;

        var browserPath = UiKit.Text(s.BrowserPath, watermark: "None");
        // "Configure" used to print the current path back and stop. There is no browser picker
        // dialog in this app, so the honest thing is to say what the field expects and focus it —
        // a fake dialog would be worse than none.
        var configure = UiKit.Button("Configure", () =>
        {
            browserPath.Focus();
            status.Text = s.BrowserPath is { Length: > 0 }
                ? "Editing the path below. Current: " + s.BrowserPath
                : "Paste the full path to chrome.exe or msedge.exe below.";
        });
            Configure = configure.Command!;

        var browserTabs = UiKit.Number(s.BrowserLimit);

        var openAs = UiKit.Combo(new[] { "Tab", "Window" }, (int)s.BrowserWindowMode);

        var profileChoices = new[] { "Browser default" }
            .Concat(s.BrowserProfiles).Distinct().ToList();
        var checkoutProfile = UiKit.Combo(profileChoices, 0);
        _checkoutProfile = checkoutProfile;   // R238: SelectedProfiles reads it

        // This used to echo whatever was already in settings. Now it looks at the disk, because
        // the whole point of the button is to notice a profile the user just created.
        var refreshProfiles = UiKit.Button("Refresh", () => Refresh.Execute(null));

        // R77: the live page prints "Round robin" with a space; Enum.GetNames gave
        // "RoundRobin", so the enum name was leaking straight into the UI.
        var assignment = UiKit.Combo(AssignmentChoices, (int)s.BrowserProfileAssignment);

        // R77: the live page prints its three headings as dim captions, not as bold card titles
        // (the same correction R75 made on five other pages), and at rest it shows six controls.
        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                UiKit.Caption("3D Secure"),
                UiKit.Row("Auto Open 3DS", auto3ds),
                // R195: AutoOpen3DSLimit had no control. The property existed, MainWindow read it
                // to cap how many 3DS windows open at once, and the value was whatever the default
                // said — 5 — forever. The original has two fields here, not one:
                //
                //   Settings.Payment.AutoOpen3DS       "Auto Open 3DS"
                //   Settings.Payment.AutoOpen3DSLimit  "Max Open"
                //      tooltip: Maximum number of 3DS windows opened automatically at once.
                //
                // R330 settled the R77 caveat on the running build: with "Auto Open 3DS" on Yes a
                // "Max Open" row appears under it (value 5); switching back to No removes it again.
                // So the row is conditional, not missing — maxOpen is built below and toggled with the combo.
                maxOpen),
            UiKit.PlainCard(
                UiKit.Caption("External Browser"),
                UiKit.Row("Browser Path", UiKit.Buttons(browserPath, configure)),
                UiKit.Row("Maximum Browser Tabs", browserTabs),
                UiKit.Row("Open Link As", openAs)),
            UiKit.PlainCard(
                UiKit.Caption("Browser Profiles"),
                UiKit.Row("Checkout Profiles", UiKit.Buttons(checkoutProfile, refreshProfiles)),
                UiKit.Row("Profile Assignment", assignment)),
            UiKit.Buttons(UiKit.Button("Save", () =>
            {
                s.AutoOpen3DS = auto3ds.SelectedIndex == 1;
                if (UiKit.TryReadInt(auto3dsLimit.Text, out var max3ds) && max3ds >= 0)
                    s.AutoOpen3DSLimit = max3ds;
                s.BrowserPath = browserPath.Text;
                if (UiKit.TryReadInt(browserTabs.Text, out var tabs)) s.BrowserLimit = tabs;
                s.BrowserWindowMode = (BrowserWindowMode)Math.Max(0, openAs.SelectedIndex);
                s.BrowserProfileAssignment =
                    (BrowserProfileAssignment)Math.Max(0, assignment.SelectedIndex);
                services.Config.Save();
                status.Text = "Saved.";
            })),
            status));
    
        Refresh = new RelayCommand(() => {
            var found = Cybersole.Services.BrowserProfileScanner.Scan();
            if (found.Count == 0)
            {
                status.Text = "No Chrome, Edge or Brave profiles found on this machine.";
                return;
            }

            s.BrowserProfiles = found;
            services.Config.Save();

            // rebuild the combo so a newly detected profile is selectable without a restart
            checkoutProfile.ItemsSource = new[] { "Browser default" }.Concat(found).Distinct().ToList();
            checkoutProfile.SelectedIndex = 0;

            status.Text = $"{found.Count} profile(s): " + string.Join(", ", found.Take(6));
        });}
}
