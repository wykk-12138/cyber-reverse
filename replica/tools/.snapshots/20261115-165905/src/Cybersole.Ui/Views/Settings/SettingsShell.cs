using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Settings;

/// <summary>
/// One entry in the settings navigation rail. <paramref name="Group"/> is non-null when the
/// entry opens a titled group in the rail (the real UI prints a small "ADVANCED" caption
/// above Captcha Providers rather than offering it as a page).
/// </summary>
public sealed record SettingsSection(string Id, string Title, Func<AppServices, Control> Build,
    string? Group = null);

/// <summary>
/// Settings shell (Cybersole.Ui.Views.Settings.SettingsView).
///
/// Order, casing and grouping were read off the running 5.18.32 build through UI Automation
/// (see docs/GUI_BASELINE.md). The real rail is:
///
///   General, Appearance, Notifications, Webhooks, Email Accounts, Google Accounts,
///   PayPal Accounts, Data,
///   —— ADVANCED ——,
///   Captcha Providers, Cloudflare Providers, Keyboard Shortcuts, Custom Stores,
///   Custom Sizes, Payment, Need Help?
///
/// with a version line and CHECK FOR UPDATES above it and Log Out below it. It is not
/// alphabetical — an earlier revision of this file sorted the ids and got the order wrong.
/// </summary>
public sealed class SettingsShell : UserControl
{
    /// <summary>
    /// R490: the original binds <c>Transition</c> on <c>Cybersole.Ui.Views.Settings.SettingsView</c> and the
    /// descriptor table marks it **Getter + Setter** — it is that type's *only* writable member (its other 18 are
    /// read-only sub-view references). This shell is the replica's counterpart of that view, so the member
    /// belongs here. What the value controls is still unverified: behaviour = Unknown.
    /// </summary>
    public string? Transition { get; set; }

    // ------------------------------------------------ copy from the image's locale (R416)
    //
    // The Settings.* values that had no counterpart in the source, captured verbatim. Keys whose pool value is
    // truncated (they end with a backslash) or longer than 100 characters are left out on purpose.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["Tooltip"] = "The corner radius of the scrollbar thumb. Higher values make the scrollbar more rounded.",   // Settings.Appearance.CornerRadius.Tooltip
        ["Tooltip2"] = "The color of the scrollbar thumb. Use a hex color code (e.g. #29293A).",   // Settings.Appearance.ScrollbarColor.Tooltip
        ["Tooltip3"] = "The width of the scrollbar in pixels. Increase this value if the scrollbar is too small to grab.",   // Settings.Appearance.ScrollbarWidth.Tooltip
        ["Title"] = "Disconnect AYCD Inbox",   // Settings.Aycd.Disconnect.Title
        ["MissingKey"] = "Enter your AYCD Inbox API key",   // Settings.Aycd.Error.MissingKey
        ["NoTaskId"] = "AYCD Inbox did not return a task id",   // Settings.Aycd.Error.NoTaskId
        ["StatusFormat"] = "AYCD Inbox returned status {0}",   // Settings.Aycd.Error.StatusFormat
        ["Unauthorized"] = "Invalid API key, or AYCD Inbox is not running",
        ["DisconnectMessage"] = "Removes your API key and stops email lookups going to AYCD Inbox. Any lookups still in flight are dropped. Your IMAP accounts are unaffected.",   // Settings.Aycd.Disconnect.Message   // Settings.Aycd.Error.Unauthorized
        ["AddSource"] = "Add Source",   // Settings.CaptchaProviders.AddSource
        ["BalanceFormat"] = "Balance ${0}",   // Settings.CaptchaProviders.BalanceFormat
        ["EmptySubtitle"] = "Add a captcha provider to get started",   // Settings.CaptchaProviders.EmptySubtitle
        ["ReorderInstructions"] = "Reorder priority from top to bottom",   // Settings.CaptchaProviders.ReorderInstructions
        ["BalanceFormat2"] = "Balance ${0}",   // Settings.CloudflareSolvers.BalanceFormat
        ["CountFormat"] = "{0} Custom Sizes",   // Settings.CustomSizes.CountFormat
        ["CountOne"] = "1 Custom Size",   // Settings.CustomSizes.CountOne
        ["CountFormat2"] = "{0} Presets",   // Settings.CustomStores.CountFormat
        ["CountOne2"] = "1 Preset",   // Settings.CustomStores.CountOne
        ["BackupIntervalTooltip"] = "Interval at which backup files will be created and saved.",   // Settings.Data.BackupIntervalTooltip
        ["MaxBackupsTooltip"] = "Maximum amount of backups to be stored.",   // Settings.Data.MaxBackupsTooltip
        ["MaxFileSizeTooltip"] = "Max file size of each log file in MB. Once this limit has been reached, file logging will stop.",   // Settings.Data.MaxFileSizeTooltip
        ["MaxRetentionTooltip"] = "Max duration that a log file will remain on the drive before being automatically deleted.",   // Settings.Data.MaxRetentionTooltip
        ["RestoreTooltip"] = "Restore all data from the selected backup file. This will overwrite all existing data.",   // Settings.Data.RestoreTooltip
        ["Tooltip4"] = "The currency to use for data analytics. Price check currency should be set in task configuration.",   // Settings.General.Currency.Tooltip
        ["Tooltip5"] = "Whether to enable the live clock in the navigation bar and which format it should use.",   // Settings.General.EnableClock.Tooltip
        ["Tooltip6"] = "Choose the display language. Changes apply immediately across the application.",   // Settings.General.Language.Tooltip
        ["Both"] = "Both:",   // Settings.General.MonitorConcurrency.Both
        ["Maximum"] = "Maximum:",   // Settings.General.MonitorConcurrency.Maximum
        ["MaximumDesc"] = "The maximum amount of monitoring tasks.",
        ["BothDesc"] = "Allows you to set both a maximum and ratio. The amount of monitoring tasks will be equal to whichever is greater.",   // Settings.General.MonitorConcurrency.BothDesc   // Settings.General.MonitorConcurrency.MaximumDesc
        ["Ratio"] = "Ratio:",   // Settings.General.MonitorConcurrency.Ratio
        ["RatioDesc"] = "The percentage of tasks that should be monitoring.",
        ["MonitorConcurrencyTooltip"] = "Configures the amount of monitoring tasks when using the \"Shared Monitor\" monitor mode.",   // Settings.General.MonitorConcurrency.Tooltip   // Settings.General.MonitorConcurrency.RatioDesc
        ["Tooltip7"] = "Which page to show on startup.",   // Settings.General.StartupPage.Tooltip
        ["UpdateChannel"] = "Update channel",
        ["UpdateChannelTooltip"] = "Release gets the public releases. Beta (staff only) gets beta builds before they're released; switching back installs the latest release.",   // Settings.General.UpdateChannel.Tooltip   // Settings.General.UpdateChannel
        ["NoProxy"] = "No proxy",   // Settings.Google.NoProxy
        ["Checking"] = "Checking...",   // Settings.Google.Status.Checking
        ["LoggedIn"] = "Logged In",   // Settings.Google.Status.LoggedIn
        ["LoggedOut"] = "Logged Out",   // Settings.Google.Status.LoggedOut
        ["GetCommunity"] = "Get help from community",   // Settings.Help.GetCommunity
        ["Connecting"] = "Connecting...",   // Settings.Imap.Status.Connecting
        ["NotSet"] = "Not Set",   // Settings.KeyBinds.NotSet
        ["AllowFormat"] = "Allow {0} Notifications",   // Settings.Notifications.AllowFormat
        ["Tooltip8"] = "Maximum amount of browser tabs to open per minute.",
        ["PaymentAssignmentTooltip"] = "How checkout links are spread over the selected profiles. Round robin cycles through them in order, Random picks one each time. Chromium-based browsers only.",   // Settings.Payment.Assignment.Tooltip
        ["AutoOpen3DSTooltip"] = "Automatically open the 3DS window when a task needs verification, instead of having to click the task status. Clicking a task status still opens its window at any time.",   // Settings.Payment.AutoOpen3DS.Tooltip
        ["AutoOpen3DSLimitTooltip"] = "Maximum number of 3DS windows opened automatically at once. The next one opens as soon as one is completed or closed. Manually clicked windows do not count.",   // Settings.Payment.AutoOpen3DSLimit.Tooltip
        ["WindowModeTooltip"] = "How an external checkout link opens. Popup and New window keep the link out of the browser window you are working in, so your active tab is never switched away.",   // Settings.Payment.WindowMode.Tooltip   // Settings.Payment.MaxTabs.Tooltip
        ["MessageFormat"] = "Are you sure you want to delete {0} sizes?\\nYou cannot undo this action.",   // Settings.Sizes.DeleteConfirm.MessageFormat
        ["TitleFormat"] = "Delete {0} presets?",   // Settings.Sizes.DeleteConfirm.TitleFormat
        ["MessageFormat2"] = "Are you sure you want to delete {0} presets?\\nYou cannot undo this action.",   // Settings.Stores.DeleteConfirm.MessageFormat
        ["TitleFormat2"] = "Delete {0} presets?",   // Settings.Stores.DeleteConfirm.TitleFormat
        ["VersionFormat"] = "Version {0}",   // Settings.VersionFormat
        ["AddButton"] = "Add Webhook",   // Settings.Webhook.AddButton
        ["EmptySubtitle2"] = "Add some webhooks to get started",   // Settings.Webhook.EmptySubtitle
        ["PaymentRequests"] = "Payment Requests",   // Settings.Webhook.Event.PaymentRequests
        ["ExtraFields"] = "Extra Fields",   // Settings.Webhook.ExtraFields
        ["Message"] = "Successfully sent a test webhook message to the webhook.",   // Settings.WebhookTest.Message
        ["Title2"] = "Test Message Sent",   // Settings.WebhookTest.Title

        ["SizesDeleteConfirmMessage"] = "Are you sure you want to delete {0} sizes?\nYou cannot undo this action.",   // Settings.Sizes.DeleteConfirm.MessageFormat
        ["StoresDeleteConfirmMessage"] = "Are you sure you want to delete {0} presets?\nYou cannot undo this action.",   // Settings.Stores.DeleteConfirm.MessageFormat
    };

    /// <summary>One of the image's settings strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    private readonly AppServices _services;
    private readonly ContentControl _host = new();
    private readonly Dictionary<string, Button> _buttons = new(StringComparer.OrdinalIgnoreCase);
    private string _current = "general";

    /// <summary>Version string shown at the top of the rail, as the real build prints it.</summary>
    public const string DisplayVersion = "5.18.32";

    public static IReadOnlyList<SettingsSection> Sections { get; } = new[]    {
        new SettingsSection("general", "General", s => new GeneralSettingsView(s)),
        new SettingsSection("appearance", "Appearance", s => new AppearanceView(s)),
        new SettingsSection("notifications", "Notifications", s => new NotificationsView(s)),
        new SettingsSection("webhooks", "Webhooks", s => new WebhookView(s)),
        new SettingsSection("email-accounts", "Email Accounts", s => new ImapView(s)),
        new SettingsSection("google-accounts", "Google Accounts", s => new GoogleAccountsView(s)),
        new SettingsSection("paypal-accounts", "PayPal Accounts", s => new PayPalAccountsView(s)),
        new SettingsSection("data", "Data", s => new DataView(s)),

        new SettingsSection("captcha-providers", "Captcha Providers",
            s => new CaptchaProvidersView(s), Group: "ADVANCED"),
        new SettingsSection("cloudflare-solvers", "Cloudflare Providers",
            s => new CloudflareSolversView(s)),
        new SettingsSection("keyboard-shortcuts", "Keyboard Shortcuts", s => new KeyBindsView(s)),
        new SettingsSection("custom-stores", "Custom Stores", s => new CustomStoresView(s)),
        new SettingsSection("custom-sizes", "Custom Sizes", s => new CustomSizesView(s)),
        new SettingsSection("payment", "Payment", s => new PaymentView(s)),
        new SettingsSection("help", "Need Help?", s => new HelpView(s)),
    };

    public string CurrentSection => _current;

    public SettingsShell(AppServices services, string? initial = null)
    {
        _services = services;

        var rail = new StackPanel { Spacing = 2, Width = 200, Margin = new Thickness(0, 0, 12, 0) };

        rail.Children.Add(BuildVersionBlock());
        rail.Children.Add(new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 8, 0, 8) });

        string? group = null;
        foreach (var section in Sections)
        {
            if (section.Group is not null && section.Group != group)
            {
                group = section.Group;
                rail.Children.Add(new TextBlock
                {
                    Text = group,
                    FontSize = 10,
                    Opacity = 0.55,
                    Margin = new Thickness(10, 10, 10, 2),
                });
            }

            var b = new Button
            {
                Content = section.Title,
                HorizontalAlignment = HorizontalAlignment.Stretch,
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Background = Brushes.Transparent,
                Padding = new Thickness(10, 6, 10, 6),
            };
            var id = section.Id;
            b.Click += (_, _) => Navigate(id);
            _buttons[id] = b;
            rail.Children.Add(b);
        }

        rail.Children.Add(new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 10, 0, 8) });

        var logout = new Button
        {
            Content = "Log Out",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Left,
            Background = Brushes.Transparent,
            Padding = new Thickness(10, 6, 10, 6),
        };
        logout.Click += (_, _) =>
        {
            _services.Auth.SignOut();
        };
        rail.Children.Add(logout);

        var scroller = new ScrollViewer { Content = rail, VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto };

        var layout = new Grid { ColumnDefinitions = new ColumnDefinitions("216,*") };
        Grid.SetColumn(scroller, 0);
        Grid.SetColumn(_host, 1);
        layout.Children.Add(scroller);
        layout.Children.Add(_host);

        Content = layout;
        Navigate(initial ?? "general");
    }

    private Control BuildVersionBlock()
    {
        var status = new TextBlock { Opacity = 0.6, FontSize = 11, TextWrapping = TextWrapping.Wrap };

        var check = new Button
        {
            Content = "CHECK FOR UPDATES",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            Padding = new Thickness(8, 5, 8, 5),
            FontSize = 11,
        };

        // Round 118: this only raised UpdateRequested, and nothing ever subscribed, so the button
        // did nothing at all. Now it performs the check itself and reports a result either way.
        //
        // Round 179: the event itself is gone. UnsubscribedEventsTests found it still declared and
        // still raised, and the raise was the only line it had left.
        check.Click += async (_, _) =>
        {
            check.IsEnabled = false;
            status.Text = "Checking…";

            try
            {
                // There is no remote feed for either build.
                //
                // R178 measured it: the original's FeedUrl points at
                // https://cdn.cybersole.io/releases/, and every Velopack path under it answers
                // 404 (RELEASES, releases.win.json, releases.json, win/, latest, index.json).
                // The same host still serves /fonts/ and /icons/ with 200 — so the CDN is up and
                // the release directory specifically is gone.
                //
                // So this is not "the replica cannot check for updates while the original can".
                // Neither can. What this button can honestly report is the local Velopack layout,
                // and even that is shared with the original install — hence "cache", not
                // "update available".
                var root = Cybersole.Core.Store.AppPaths.LocalRoot;
                var packages = Path.Combine(root, "packages");
                var cached = Directory.Exists(packages)
                    ? Directory.GetDirectories(packages).Length
                    : 0;

                await Task.Delay(350).ConfigureAwait(true);

                status.Text = cached > 0
                    ? $"Version {Cybersole.Core.Store.AppVersion.Current} — {cached} package(s) "
                      + "in the local cache. The vendor's release feed answers 404, so there is "
                      + "nothing to compare against."
                    : $"Version {Cybersole.Core.Store.AppVersion.Current} — source build, "
                      + "and the vendor's release feed answers 404.";
            }
            catch (Exception ex)
            {
                status.Text = "Update check failed: " + ex.Message;
            }
            finally
            {
                check.IsEnabled = true;
            }
        };

        return new StackPanel
        {
            Spacing = 6,
            Margin = new Thickness(4, 4, 4, 0),
            Children =
            {
                new TextBlock { Text = "Version " + DisplayVersion, Opacity = 0.7 },
                check,
                status,
            },
        };
    }

    /// <summary>
    /// The header each page prints, read off the live 5.18.32 build in R74. Only the four pages that
    /// were walked have one; the rest fall back to their nav label with no subtitle, which is what
    /// an unvisited page honestly is.
    ///
    /// <para>
    /// The rail and the page disagree on purpose in one place: the rail says "Captcha Providers"
    /// and the page is titled "3rd Party Captcha Providers".
    /// </para>
    /// </summary>
    public static readonly IReadOnlyDictionary<string, (string Title, string Subtitle)> PageHeaders =
        new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase)
        {
            // R74 read four pages; R75 swept the other eleven in one pass. Every page now has the
            // header the live build prints, word for word.
            ["general"] = ("General", "Profile, delays, and other general preferences"),
            ["appearance"] = ("Appearance", "Customize scrollbar appearance and sizing"),
            ["notifications"] = ("Notifications", "Notifications and sounds"),
            ["webhooks"] = ("Webhooks", "Receive real time notifications into your favorite services"),
            ["email-accounts"] = ("Email Accounts",
                                  "Add imap email accounts to automatically login to certain sites"),
            ["google-accounts"] = ("Google Accounts",
                                   "Store Google accounts for easy access when using solvers"),
            ["paypal-accounts"] = ("PayPal Accounts",
                                   "Store PayPal accounts for easy access when creating tasks"),
            ["data"] = ("Data", "Import, export and backup data"),

            ["captcha-providers"] = ("3rd Party Captcha Providers",
                                     "Add and configure 3rd party captcha solving services"),
            ["cloudflare-solvers"] = ("3rd Party Cloudflare Providers",
                                      "Add Cloudflare solving services, then pick one per task group"),
            ["keyboard-shortcuts"] = ("Keyboard Shortcuts", "Edit and disable keyboard shortcuts"),
            ["custom-stores"] = ("Custom Stores", "Add custom Shopify store presets for easy access"),
            ["custom-sizes"] = ("Custom Sizes", "Add custom Shopify size presets for easy access"),
            ["payment"] = ("Payment", "Configure advanced payment settings"),
            ["help"] = ("Get Help", "Take a look at common errors or contact support"),
        };

    /// <summary>
    /// The three rail entries whose page carries a different title. Kept as a set so a test can
    /// assert the count: if a future round "tidies" one of them into agreement, this list shrinks
    /// and so should the test, deliberately.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> RailAndPageDisagree =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["captcha-providers"] = "3rd Party Captcha Providers",
            ["cloudflare-solvers"] = "3rd Party Cloudflare Providers",
            ["help"] = "Get Help",
        };

    /// <summary>
    /// The count caption each list-shaped page prints above its rows. The original's wording is
    /// per page, not one shared "{0} items": "0 Presets" for stores, "0 Custom Sizes" for sizes,
    /// "0 Accounts" for the three account pages.
    /// </summary>
    public static string ListCountCaption(string sectionId, int count) => sectionId switch
    {
        "custom-stores" => $"{count} Presets",
        "custom-sizes" => $"{count} Custom Sizes",
        "email-accounts" or "google-accounts" or "paypal-accounts" => $"{count} Accounts",
        _ => count.ToString(),
    };

    /// <summary>The header a section prints: its own if it was walked, else its nav label.</summary>
    public static (string Title, string? Subtitle) PageHeaderFor(string id)
    {
        if (PageHeaders.TryGetValue(id, out var header)) return (header.Title, header.Subtitle);
        var section = Sections.FirstOrDefault(s => string.Equals(s.Id, id, StringComparison.OrdinalIgnoreCase));
        return (section?.Title ?? id, null);
    }

    /// <summary>Switch to a section by id. Unknown ids are ignored.</summary>
    public void Navigate(string id)
    {
        var section = Sections.FirstOrDefault(s => string.Equals(s.Id, id, StringComparison.OrdinalIgnoreCase));
        if (section is null) return;

        _current = section.Id;
        foreach (var (key, button) in _buttons)
            button.FontWeight = string.Equals(key, section.Id, StringComparison.OrdinalIgnoreCase)
                ? FontWeight.SemiBold
                : FontWeight.Normal;

        var view = section.Build(_services);
        var header = PageHeaderFor(section.Id);
        _host.Content = header.Subtitle is null
            ? view
            : UiKit.Page(header.Title, header.Subtitle, view);
    }

    /// <summary>Build every section once — used by tests to prove each view constructs.</summary>
    public static IReadOnlyList<(string Id, Control View)> BuildAll(AppServices services) =>
        Sections.Select(s => (s.Id, s.Build(services))).ToList();
}
