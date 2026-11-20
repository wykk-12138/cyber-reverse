using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Services.Captcha;

namespace Cybersole.Ui.Views.Settings.Modals;

/// <summary>Cybersole.Ui.Views.Settings.Modals.ImapCreatorView — Close / Save.</summary>
public sealed class ImapCreatorView : SettingsModal
{
    public ImapCreatorView(AppServices services) : base("New email account", 480, 420)
    {
        var host = UiKit.Text(watermark: "imap.gmail.com");
        var port = UiKit.Number(993);
        var user = UiKit.Text(watermark: "you@example.com");
        var pass = UiKit.Text(password: true);
        var ssl = UiKit.Check("Use SSL", true);

        Body.Children.Add(UiKit.Row("Host", host));
        Body.Children.Add(UiKit.Row("Port", port));
        Body.Children.Add(UiKit.Row("Username", user));
        Body.Children.Add(UiKit.Row("Password", pass));
        Body.Children.Add(UiKit.Row("TLS", ssl));

        BuildFooter(SaveButton(() =>
        {
            if (string.IsNullOrWhiteSpace(host.Text) || string.IsNullOrWhiteSpace(user.Text))
                throw new InvalidOperationException("Host and username are required.");

            services.Config.Accounts.Imap.Add(new ImapAccount
            {
                Host = host.Text!,
                Port = UiKit.TryReadInt(port.Text, out var p) ? p : 993,
                User = user.Text!,
                Password = pass.Text ?? string.Empty,
                UseSsl = ssl.IsChecked == true,
            });
            services.Config.Save();
        }));
    }
}

/// <summary>Cybersole.Ui.Views.Settings.Modals.AycdInboxCreatorView — Close / Save.</summary>
public sealed class AycdInboxCreatorView : SettingsModal
{
    public AycdInboxCreatorView(AppServices services) : base("AYCD Inbox", 480, 380)
    {
        var aycd = services.Config.Accounts.AycdInbox;

        var key = UiKit.Text(aycd.ApiKey, watermark: "API key");
        ToolTip.SetTip(key, "Found in the AYCD Inbox app under Settings > Integrations > Inbox API. Inbox must be running for the key to work.");
        var group = UiKit.Text(aycd.AppGroup, watermark: "group id");
        var template = UiKit.Text(aycd.TemplateId, watermark: "Leave blank to use the default template");
        var timeout = UiKit.Number(aycd.TimeoutSeconds);
        var enabled = UiKit.Check("Enabled", aycd.Enabled);

        Body.Children.Add(UiKit.Row("API key", key));
        Body.Children.Add(UiKit.Row("Group", group));
        Body.Children.Add(UiKit.Row("Template", template));
        Body.Children.Add(UiKit.Row("Timeout (s)", timeout));
        Body.Children.Add(UiKit.Row("State", enabled));

        BuildFooter(SaveButton(() =>
        {
            aycd.ApiKey = key.Text;
            aycd.AppGroup = group.Text;
            aycd.TemplateId = template.Text;
            if (UiKit.TryReadInt(timeout.Text, out var t)) aycd.TimeoutSeconds = t;
            aycd.Enabled = enabled.IsChecked == true;
            services.Config.Save();
        }));
    }
}

/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.CaptchaProviderCreatorView —
/// Close / Creating / Delete / Properties / Save.
/// </summary>
public sealed class CaptchaProviderCreatorView : SettingsModal
{

    /// <summary>True while this dialog is creating a new provider rather than editing one (bound as <c>Creating</c>).</summary>
    public bool Creating { get; private set; }
    public CaptchaProviderCreatorView(AppServices services, CaptchaProviderConfig? existing = null)
        : base(existing is null ? "New captcha provider" : $"Edit {existing.Name}", 520, 500)
    {
        Creating = existing is null;
        var registry = services.Captcha.Registry;
        var target = existing ?? new CaptchaProviderConfig();

        var type = UiKit.Combo(registry.Drivers.Select(d => d.Type).ToList(),
            Math.Max(0, registry.Drivers.Select((d, i) => (d, i))
                .FirstOrDefault(x => x.d.Type == target.Type).i));
        var name = UiKit.Text(target.Name, watermark: "Provider name");
        var apiKey = UiKit.Text(target.ApiKey, watermark: "API key", password: true);
        var concurrency = UiKit.Number(target.Concurrency);
        ToolTip.SetTip(concurrency, "This is how many simultaneous solves are allowed");
        var priority = UiKit.Number(target.Priority);
        var enabled = UiKit.Check("Enabled", target.Enabled);
        var creating = new TextBlock { Text = existing is null ? "new" : "editing", Opacity = 0.6 };

        // R1285: Type has no setter in the image (1432159DC getter, no setter), so an existing row
        // cannot change its source — the combo is read-only when editing.
        if (existing is not null) type.IsEnabled = false;
        Body.Children.Add(UiKit.Row("Type", type));
        Body.Children.Add(UiKit.Row("Name", name));
        Body.Children.Add(UiKit.Row("API key", apiKey));
        Body.Children.Add(UiKit.Row("Concurrency", concurrency));
        Body.Children.Add(UiKit.Row("Priority", priority));
        Body.Children.Add(UiKit.Row("State", enabled));
        Body.Children.Add(UiKit.Row("Mode", creating));

        var drivers = registry.Drivers;
        if (type.SelectedIndex >= 0 && type.SelectedIndex < drivers.Count)
        {
            var driver = drivers.ElementAt(type.SelectedIndex);
            var props = new ListBox
            {
                Height = 90,
                ItemsSource = new List<string>
                {
                    $"type: {driver.Type}",
                    $"name: {driver.Name}",
                    $"balance supported: {driver.BalanceSupported}",
                    $"kinds: {string.Join(", ", driver.Kinds)}",
                },
            };
            Body.Children.Add(UiKit.Row("Properties", props));
        }

        var save = SaveButton(() =>
        {
            // R1285: only creation picks a Type. An existing row keeps the source it was opened with,
            // because the image gives that property a getter and no setter.
            var row = existing is null
                ? new CaptchaProviderConfig
                {
                    Type = drivers.Count > 0 && type.SelectedIndex >= 0
                        ? drivers.ElementAt(type.SelectedIndex).Type
                        : target.Type,
                }
                : target;

            row.Name = string.IsNullOrWhiteSpace(name.Text) ? row.Type : name.Text!;
            row.ApiKey = apiKey.Text;
            if (UiKit.TryReadInt(concurrency.Text, out var c)) row.Concurrency = c;
            if (UiKit.TryReadInt(priority.Text, out var p)) row.Priority = p;
            row.Enabled = enabled.IsChecked == true;

            if (existing is null) registry.AddConfig(row);
            services.Config.Save();
        });
        BuildFooter(save,
            DeleteButton(() =>
            {
                if (existing is null) return;
                registry.RemoveConfig(existing);
                services.Config.Save();
            }));
    }
}

/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.CloudflareSolverCreatorView —
/// Close / Creating / Delete / Save.
/// </summary>
public sealed class CloudflareSolverCreatorView : SettingsModal
{
    /// <summary>Bound as <c>Save</c>: the same command the SaveButton button carries.</summary>
    public ICommand Save { get; }

    /// <summary>Bound as <c>Delete</c>: the same command the DeleteButton button carries.</summary>
    public ICommand Delete { get; }



    /// <summary>True while this dialog is creating a new provider rather than editing one (bound as <c>Creating</c>).</summary>
    public bool Creating { get; private set; }
    public CloudflareSolverCreatorView(AppServices services) : base("New Cloudflare solver", 480, 380)
    {
        var registry = services.Captcha.Registry;
        var target = new CaptchaProviderConfig { Type = "cfsolver", Name = "CfSolver" };

        var name = UiKit.Text(target.Name, watermark: "Solver name");
        var apiKey = UiKit.Text(watermark: "API key", password: true);
        var concurrency = UiKit.Number(5);
        ToolTip.SetTip(concurrency, "How many solves can run at once. Keep it at or below your plan's limit.");
        var creating = new TextBlock { Text = "new", Opacity = 0.6 };

        Body.Children.Add(UiKit.Row("Name", name));
        Body.Children.Add(UiKit.Row("API key", apiKey));
        Body.Children.Add(UiKit.Row("Concurrency", concurrency));
        Body.Children.Add(UiKit.Row("Mode", creating));
        Body.Children.Add(UiKit.Caption(
            "CfSolver runs at https://cf-solver.cybersole.io and only handles turnstile."));

                var save = SaveButton(() =>
        {
            target.Name = string.IsNullOrWhiteSpace(name.Text) ? "CfSolver" : name.Text!;
            target.ApiKey = apiKey.Text;
            if (UiKit.TryReadInt(concurrency.Text, out var c)) target.Concurrency = c;
            target.Enabled = !string.IsNullOrEmpty(target.ApiKey);
            registry.AddConfig(target);
            services.Config.Save();
        });
        Save = save.Command!;
        var delete = DeleteButton(() => { /* nothing persisted yet */ });
        Delete = delete.Command!;
BuildFooter(save,
            delete);
    }
}

/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.GoogleAccountEditView —
/// Account / AccountName / Close / EditMode / Proxy / Save.
/// </summary>
public sealed class GoogleAccountEditView : SettingsModal
{
    /// <summary>Bound as <c>Save</c>: the same command the SaveButton button carries.</summary>
    public ICommand Save { get; }


    // R257: the original binds AccountName / EditMode here (analysis/xaml_bindings.json).

    /// <summary>The display name typed into the dialog (bound as <c>AccountName</c>).</summary>
    public string AccountName { get; set; } = string.Empty;

    /// <summary>True when editing an existing account rather than creating one (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

    /// <summary>Records whether this dialog is an edit (the constructor decides).</summary>
    private void SetEditMode(bool editing) => EditMode = editing;


    /// <summary>Proxy string for this account (bound as <c>Proxy</c>); reads and writes the widget.</summary>
    public string Proxy
    {
        get => _proxy.Text ?? string.Empty;
        set => _proxy.Text = value ?? string.Empty;
    }

    private readonly TextBox _proxy;

    public GoogleAccountEditView(AppServices services, GoogleAccount? existing = null)
        : base(existing is null ? "New Google account" : "Edit Google account", 480, 380)
    {
        SetEditMode(existing is not null);
        AccountName = existing?.Name ?? string.Empty;
        var doc = services.Config.Accounts;

        var account = UiKit.Text(existing?.Email, watermark: "name@gmail.com");
        var accountName = UiKit.Text(existing?.Name, watermark: "Display name");
        _proxy = UiKit.Text(existing?.Proxy, watermark: "host:port:user:pass");
        var editMode = new TextBlock { Text = existing is null ? "create" : "edit", Opacity = 0.6 };

        Body.Children.Add(UiKit.Row("Account", account));
        Body.Children.Add(UiKit.Row("Account name", accountName));
        Body.Children.Add(UiKit.Row("Proxy", _proxy));
        Body.Children.Add(UiKit.Row("Mode", editMode));

                var save = SaveButton(() =>
        {
            if (string.IsNullOrWhiteSpace(account.Text))
                throw new InvalidOperationException("Account email is required.");

            if (existing is null)
            {
                doc.Google.Add(new GoogleAccount
                {
                    Email = account.Text!,
                    Name = accountName.Text,
                    Proxy = _proxy.Text,
                });
            }
            else
            {
                existing.Email = account.Text!;
                existing.Name = accountName.Text;
                existing.Proxy = _proxy.Text;
            }
            services.Config.Save();
        });
        Save = save.Command!;
BuildFooter(save);
    }
}

/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.PayPalAccountCreatorView —
/// AutoReopen / Close / EditMode / InactivateAfter / Model / Password / ProxyGroup / Save /
/// UseLoginProxy.
/// </summary>
public sealed class PayPalAccountCreatorView : SettingsModal
{
    // R257: the original binds EditMode / InactivateAfter here (analysis/xaml_bindings.json).

    /// <summary>True when editing an existing account (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

    /// <summary>Records whether this dialog is an edit (the constructor decides).</summary>
    private void SetEditMode(bool editing) => EditMode = editing;

    /// <summary>The inactivity window after which the session is dropped (bound as <c>InactivateAfter</c>).</summary>
    public string InactivateAfter { get; set; } = "Permanent";


    // R520: the four widgets the original binds by name. The getter writes through to the widget, so there is no
    // second copy to keep in sync and a later assignment shows up on screen immediately.
    /// <summary>PayPal password (bound as <c>Password</c>).</summary>
    public string Password
    {
        get => _password.Text ?? string.Empty;
        set => _password.Text = value ?? string.Empty;
    }

    /// <summary>Proxy group name (bound as <c>ProxyGroup</c>).</summary>
    public string ProxyGroup
    {
        get => _proxyGroup.Text ?? string.Empty;
        set => _proxyGroup.Text = value ?? string.Empty;
    }

    /// <summary>Whether checkout goes out through the account's login proxy (bound as <c>UseLoginProxy</c>).</summary>
    public bool UseLoginProxy
    {
        get => _useLoginProxy.IsChecked == true;
        set => _useLoginProxy.IsChecked = value;
    }

    /// <summary>Whether the session reopens after a drop (bound as <c>AutoReopen</c>).</summary>
    public bool AutoReopen
    {
        get => _autoReopen.IsChecked == true;
        set => _autoReopen.IsChecked = value;
    }

    /// <summary>Bound as <c>Save</c>: the same body the footer button runs.</summary>
    public ICommand Save { get; }

    private readonly TextBox _model;
    private readonly TextBox _password;
    private readonly TextBox _proxyGroup;
    private readonly CheckBox _useLoginProxy;
    private readonly CheckBox _autoReopen;
    private readonly PayPalAccount? _existing;
    private readonly AccountsDocument _doc;
    private readonly AppServices _services;

    public PayPalAccountCreatorView(AppServices services, PayPalAccount? existing = null)
        : base(existing is null ? "New PayPal account" : "Edit PayPal account", 500, 480)
    {
        _services = services;
        _existing = existing;
        _doc = services.Config.Accounts;

        _model = UiKit.Text(existing?.Email, watermark: "paypal email");
        _password = UiKit.Text(password: true);
        _proxyGroup = UiKit.Text(existing?.ProxyGroup, watermark: "proxy group");
        _useLoginProxy = UiKit.Check("Use login proxy", existing?.UseLoginProxy ?? true);
        _autoReopen = UiKit.Check("Auto reopen", existing?.AutoReopen ?? false);
        // Live dialog offers a labelled dropdown, defaulting to Permanent.
        var durations = new[] { "Permanent", "5 minutes", "15 minutes", "30 minutes", "1 hour" };
        var current = existing?.MaxInactiveSessionDuration ?? "Permanent";
        var durationIndex = Math.Max(0, Array.IndexOf(durations, current));
        var inactivateAfter = UiKit.Combo(durations, durationIndex);
        var editMode = new TextBlock { Text = existing is null ? "create" : "edit", Opacity = 0.6 };

        Body.Children.Add(UiKit.Row("Model", _model));
        Body.Children.Add(UiKit.Row("Password", _password));
        Body.Children.Add(UiKit.Row("Proxy group", _proxyGroup));
        Body.Children.Add(UiKit.Row("Use login proxy", _useLoginProxy));
        Body.Children.Add(UiKit.Row("Auto reopen", _autoReopen));
        Body.Children.Add(UiKit.Row("Inactivate after (min)", inactivateAfter));
        Body.Children.Add(UiKit.Row("Mode", editMode));

        Save = new RelayCommand(SaveCore);
        BuildFooter(SaveButton(SaveCore));
    }

    /// <summary>Validates and persists; the footer's Save button and the bound <c>Save</c> both run this.</summary>
    private void SaveCore()
    {
        if (string.IsNullOrWhiteSpace(_model.Text))
            throw new InvalidOperationException("A PayPal email is required.");

        var target = _existing ?? new PayPalAccount();
        target.Email = _model.Text!;
        target.ProxyGroup = _proxyGroup.Text;
        target.UseLoginProxy = _useLoginProxy.IsChecked == true;
        target.AutoReopen = _autoReopen.IsChecked == true;
        target.LastRefresh = DateTime.UtcNow;

        if (_existing is null) _doc.PayPal.Add(target);
        _services.Config.Save();
    }
}

/// <summary>
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
    public static readonly string EmptyTitle = Common.EmptyView.Headline;
    public const string EmptySubtitle = "Search a valid product URL";

    private readonly AppServices _services;
    private readonly Action? _onChanged;
    private readonly List<string> _discovered = new();
    private readonly StackPanel _found = new() { Spacing = 2 };
    private readonly StackPanel _empty;
    private readonly Border _listHost;
    private readonly TextBlock _status = UiKit.Status();

    // ------------------------------------------------ bound members (R239)
    //
    // The original binds SizeOptions / ToggleSizeSelected on SizeCreatorView (analysis/xaml_bindings.json).
    // SizeOptions is the catalogue this dialog offers; ToggleSizeSelected flips one entry in the pick list.

    /// <summary>The sizes on offer here — the same ladder the task editor uses (bound as <c>SizeOptions</c>).</summary>
    public IReadOnlyList<string> SizeOptions =>
        Cybersole.Core.Models.SizePalette.Build(_services.Config.Settings.CustomSizes);

    /// <summary>Adds the size to the found list, or removes it if it is already there (bound as <c>ToggleSizeSelected</c>).</summary>
    public bool ToggleSizeSelected(string size)
    {
        if (string.IsNullOrWhiteSpace(size)) return false;

        var trimmed = size.Trim();
        if (_discovered.RemoveAll(s => string.Equals(s, trimmed, StringComparison.OrdinalIgnoreCase)) > 0)
            return false;   // removed

        _discovered.Add(trimmed);
        return true;        // added
    }

    /// <summary>What has been picked so far, in order.</summary>
    public IReadOnlyList<string> SelectedSizes => _discovered;

    public SizeCreatorView(AppServices services, Action? onChanged = null) : base(DialogTitle, 620, 430)
    {
        _services = services;
        _onChanged = onChanged;

        var url = UiKit.Text(watermark: "https://cybersole.io/");
        var status = UiKit.Status();

        _empty = new StackPanel
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
        };

        _listHost = new Border
        {
            MinHeight = 170,
            Padding = new Thickness(10),
            BorderThickness = new Thickness(1),
            BorderBrush = new Avalonia.Media.SolidColorBrush(
                Avalonia.Media.Color.Parse("#2A2E3A")),
            CornerRadius = new CornerRadius(6),
            Child = _empty,
        };

        ShowList();

        var search = new Button
        {
            Content = "Search",
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
            HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center,
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
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
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

    /// <summary>Renders the discovered sizes, or the empty pane when there are none.</summary>
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

/// <summary>
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
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
            HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center,
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

/// <summary>
/// The "New Webhook" form (Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView).
///
/// <para>
/// Laid out from the running 5.18.32 build (R339): Name and Platform share a row, the URL sits under a "Webhook"
/// caption, and the footer button names the first thing that is not right yet (R340) — "Enter name" while the name box
/// is empty, "Enter valid webhook" while the URL does not parse, "Save" once both are good, and only that last state is
/// enabled. All three labels were read off the live modal.
/// </para>
/// </summary>
public sealed class WebhookCreatorView : SettingsModal
{
    /// <summary>
    /// The submit button's text, measured on the running build (R340): it names the first thing that is wrong —
    /// <c>Enter name</c> while the name is empty, <c>Enter valid webhook</c> while the URL does not parse, and
    /// <c>Save</c> once both are good. The button is only enabled in the last state.
    /// </summary>
    public static string SubmitLabel(string? name, string? url)
    {
        if (string.IsNullOrWhiteSpace(name)) return "Enter name";
        if (!IsWebhookUrl(url)) return "Enter valid webhook";
        return "Save";
    }

    /// <summary>True when the text is an absolute http(s) URL — what the live form accepts before enabling Save.</summary>
    public static bool IsWebhookUrl(string? url) =>
        !string.IsNullOrWhiteSpace(url)
        && Uri.TryCreate(url.Trim(), UriKind.Absolute, out var uri)
        && (uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps);

    /// <summary>Bound as <c>Save</c>: the same command instance the Save button carries.</summary>
    public ICommand Save { get; }

    public WebhookCreatorView(AppServices services) : base("New Webhook", 500, 400)
    {
        var name = UiKit.Text(watermark: "Personal server");
        var url = UiKit.Text(watermark: "https://discord.com/api/webhooks");
        var platform = UiKit.Combo(new[] { "Select provider", "Discord", "Custom" });
        var group = UiKit.Combo(services.Config.TaskGroups.Select(g => g.Name).ToList());
        var events = new StackPanel { Spacing = 2 };
        foreach (var evt in new[] { "Checkouts", "Declines", "PayPal", "Payment requests", "Smart actions" })
            events.Children.Add(UiKit.Check(evt, true));

        // Name and Platform share a row on the live modal; the URL sits below them under its own caption.
        var pair = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*") };
        pair.Children.Add(UiKit.Row("Name", name));
        var platformRow = UiKit.Row("Platform", platform);
        Grid.SetColumn(platformRow, 2);
        pair.Children.Add(platformRow);

        Body.Children.Add(pair);
        Body.Children.Add(UiKit.Caption("Webhook"));
        Body.Children.Add(url);
        Body.Children.Add(UiKit.Row("Attach to group", group));
        Body.Children.Add(UiKit.Row("Events", UiKit.Scroll(events)));

        var save = SaveButton(() =>
        {
            if (!IsWebhookUrl(url.Text))
                throw new InvalidOperationException("A webhook URL is required.");

            var webhook = new Webhook
            {
                Name = string.IsNullOrWhiteSpace(name.Text) ? "Webhook" : name.Text!,
                Url = url.Text!,
                // R342: the platform combo and the event checkboxes were collected and then dropped; the binding
                // table says IWebhook carries both (Type, Events), so they are stored now.
                Type = platform.SelectedIndex > 0 && platform.SelectedItem is string chosen ? chosen : string.Empty,
            };

            foreach (var box in events.Children.OfType<CheckBox>())
                if (box.IsChecked == true && box.Content is string label)
                    webhook.Events.Add(label);
            services.Config.Settings.Webhooks.Add(webhook);

            var index = Math.Clamp(group.SelectedIndex, 0, Math.Max(0, services.Config.TaskGroups.Count - 1));
            if (services.Config.TaskGroups.Count > 0)
                services.Config.TaskGroups[index].Webhooks.Add(webhook);

            services.Config.Save();
        });
        Save = save.Command!;

        BuildFooter(save);

        void Relabel()
        {
            save.Content = SubmitLabel(name.Text, url.Text);
            save.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        }
        name.TextChanged += (_, _) => Relabel();
        url.TextChanged += (_, _) => Relabel();
        Relabel();
    }
}

/// <summary>
/// Cybersole.Ui.Views.Settings.Modals.ShippingRatesCreatorView — per-group shipping rate
/// table used by the checkout forms.
/// </summary>
public sealed class ShippingRatesCreatorView : SettingsModal
{
    public ShippingRatesCreatorView(AppServices services) : base("Shipping rates", 520, 420)
    {
        var group = UiKit.Combo(services.Config.TaskGroups.Select(g => g.Name).ToList());
        var method = UiKit.Text(watermark: "Standard");
        var price = UiKit.Text(watermark: "0.00");
        var rows = new ListBox { Height = 120 };
        var rates = new List<(string Method, string Price)>();

        void Refresh() => rows.ItemsSource = rates.Select(r => $"{r.Method} — {r.Price}").ToList();
        Refresh();

        Body.Children.Add(UiKit.Row("Task group", group));
        Body.Children.Add(UiKit.Row("Method", method));
        Body.Children.Add(UiKit.Row("Price", price));
        Body.Children.Add(UiKit.Row("Rates", rows));

        BuildFooter(
            UiKit.Button("Add rate", () =>
            {
                if (string.IsNullOrWhiteSpace(method.Text))
                {
                    SetStatus("A method name is required.");
                    return;
                }
                rates.Add((method.Text!, price.Text ?? "0.00"));
                Refresh();
                SetStatus($"{rates.Count} rate(s).");
            }),
            SaveButton(() =>
            {
                var index = Math.Clamp(group.SelectedIndex, 0, Math.Max(0, services.Config.TaskGroups.Count - 1));
                if (services.Config.TaskGroups.Count == 0) return;
                services.Config.TaskGroups[index].ShippingRate = rates.Count > 0
                    ? $"{rates[0].Method}:{rates[0].Price}"
                    : null;
                services.Config.Save();
            }));
    }
}
