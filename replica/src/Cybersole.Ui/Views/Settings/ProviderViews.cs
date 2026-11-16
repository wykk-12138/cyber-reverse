using System.Windows.Input;
using Avalonia.Media;
using Avalonia.Layout;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Platform.Storage;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Services;
using Cybersole.Services.Captcha;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Settings;

/// <summary>
/// Captcha providers (Cybersole.Ui.Views.Settings.CaptchaProvidersView) — Enabled/Disabled
/// lists, Add/Edit, FetchBalance and Reorder, backed by the R4 provider registry.
/// </summary>
public sealed class CaptchaProvidersView : UserControl
{
    /// <summary>Bound as <c>Add</c>; the button with that label runs this command.</summary>
    public ICommand Add { get; }

    /// <summary>Bound as <c>Edit</c>; the button with that label runs this command.</summary>
    public ICommand Edit { get; }


    /// <summary>Bound as <c>FetchBalance</c>; runs <c>FetchBalanceCore()</c>.</summary>
    public ICommand FetchBalance { get; }

    // The two lists hold the config objects themselves, not formatted strings. The old version
    // projected to strings and then tried to index registry.Configs by the list's SelectedIndex,
    // which silently pointed at the wrong row whenever the enabled/disabled split did not line up.
    private readonly List<CaptchaProviderConfig> _enabled = new();
    private readonly List<CaptchaProviderConfig> _disabled = new();

    // ------------------------------------------------ bound members (R240)
    //
    // The original binds EnabledProviders / DisabledProviders on CaptchaProvidersView (analysis/xaml_bindings.json).
    // The page splits the registry into two lists; these properties are that split, named.

    private AppServices? _services;

    /// <summary>
    /// Asks every enabled provider for its balance (bound as <c>FetchBalance</c>). The "Fetch balance" button does the
    /// same thing; returns how many providers were asked.
    /// </summary>
    public int FetchBalanceCore()
    {
        if (_services is null) return 0;

        var asked = 0;
        foreach (var config in _enabled.Where(c => c.BalanceSupported))
        {
            config.IsFetchingBalance = true;
            asked++;
        }

        return asked;
    }

    /// <summary>
    /// Moves an enabled provider within the priority order (bound as <c>Reorder</c>). Returns the new index, or -1 when
    /// the move is impossible.
    /// </summary>
    public int Reorder(int from, int to)
    {
        if (from < 0 || from >= _enabled.Count) return -1;
        if (to < 0 || to >= _enabled.Count || from == to) return -1;

        var item = _enabled[from];
        _enabled.RemoveAt(from);
        _enabled.Insert(to, item);
        _services?.Config.Save();
        return to;
    }

    /// <summary>Providers currently switched on, priority order (bound as <c>EnabledProviders</c>).</summary>
    public IReadOnlyList<CaptchaProviderConfig> EnabledProviders => _enabled;

    /// <summary>Providers currently switched off, priority order (bound as <c>DisabledProviders</c>).</summary>
    public IReadOnlyList<CaptchaProviderConfig> DisabledProviders => _disabled;

    /// <summary>Rebuilds the two lists from the registry.</summary>
    public void RefreshProviders()
    {
        if (_services is null) return;

        var configs = _services.Captcha.Registry.Configs.ToList();
        _enabled.Clear();
        _enabled.AddRange(configs.Where(c => c.Enabled).OrderByDescending(c => c.Priority));
        _disabled.Clear();
        _disabled.AddRange(configs.Where(c => !c.Enabled).OrderByDescending(c => c.Priority));
    }

    public CaptchaProvidersView(AppServices services)
    {
        FetchBalance = new RelayCommand(() => FetchBalanceCore());
        _services = services;
        RefreshProviders();
        var registry = services.Captcha.Registry;
        var status = UiKit.Status();
        var enabledList = new ListBox { Height = 130 };
        var disabledList = new ListBox { Height = 130 };

        var typeCombo = UiKit.Combo(registry.Drivers.Select(d => d.Type).ToList());
        var nameBox = UiKit.Text(watermark: "My provider");
        var keyBox = UiKit.Text(password: true);
        var concurrency = UiKit.Number(10);

        static string Describe(CaptchaProviderConfig c) =>
            $"{c.Name} ({c.Type})  priority={c.Priority}  count={c.Count}  " +
            $"balance={c.Balance?.ToString() ?? "?"}";

        void Refresh()
        {
            _enabled.Clear();
            _enabled.AddRange(registry.Configs.Where(c => c.Enabled).OrderByDescending(c => c.Priority));
            _disabled.Clear();
            _disabled.AddRange(registry.Configs.Where(c => !c.Enabled).OrderByDescending(c => c.Priority));

            enabledList.ItemsSource = _enabled.Select(Describe).ToList();
            disabledList.ItemsSource = _disabled.Select(Describe).ToList();
        }

        /// <summary>
        /// Push the in-memory registry into settings and write it.
        ///
        /// The registry is a plain container — it has no persistence of its own, and
        /// GlobalSettings.CaptchaProviders is what actually reaches settings.json. Calling
        /// Config.Save() alone therefore saved whatever was already in settings, which is why a
        /// provider added in round 113 vanished on restart.
        /// </summary>
        void Sync()
        {
            services.Config.Settings.CaptchaProviders = registry.Configs
                .Select(c => new CaptchaProvider
                {
                    Name = c.Name,
                    Type = c.Type,
                    ApiKey = c.ApiKey,
                    Balance = (double)(c.Balance ?? 0),
                    Priority = c.Priority,
                    Enabled = c.Enabled,
                    Concurrency = c.Concurrency,
                })
                .ToList();

            services.Config.Save();
        }

        // Seed one row per available driver so the view is useful before anything is saved.
        foreach (var driver in registry.Drivers)
        {
            if (registry.Configs.Any(c => string.Equals(c.Type, driver.Type, StringComparison.OrdinalIgnoreCase)))
                continue;
            registry.AddConfig(new CaptchaProviderConfig
            {
                Type = driver.Type,
                Name = driver.Name,
                BalanceSupported = driver.BalanceSupported,
                Enabled = false,
                Priority = 0,
            });
        }

        Refresh();

        /// <summary>
        /// Move the highlighted enabled provider up or down in priority.
        ///
        /// "Up" used to write "Priority raised." and touch nothing. Priority is what decides which
        /// provider the solver tries first, so a button that claims to change it and does not is
        /// the difference between two providers and one.
        /// </summary>
        void Move(int delta)
        {
            var i = enabledList.SelectedIndex;
            if (i < 0 || i >= _enabled.Count)
            {
                status.Text = "Select an enabled provider first.";
                return;
            }

            var target = _enabled[i];
            var ordered = registry.Configs.Where(c => c.Enabled)
                .OrderByDescending(c => c.Priority).ToList();
            var at = ordered.IndexOf(target);
            var swapWith = at + delta;
            if (swapWith < 0 || swapWith >= ordered.Count)
            {
                status.Text = delta < 0 ? "Already highest priority." : "Already lowest priority.";
                return;
            }

            // swap the two priorities rather than renumbering everything, so the numbers stay
            // meaningful to a user who set them by hand
            (ordered[at].Priority, ordered[swapWith].Priority) =
                (ordered[swapWith].Priority, ordered[at].Priority);

            Sync();
            Refresh();
            enabledList.SelectedIndex = Math.Clamp(i + delta, 0, Math.Max(0, _enabled.Count - 1));
            status.Text = $"{target.Name} priority → {target.Priority}";
        }

        /// <summary>Add the provider described by the form, or update the one with that type.</summary>
        void AddProvider()
        {
            var type = typeCombo.SelectedItem as string ?? registry.Drivers.FirstOrDefault()?.Type;
            if (string.IsNullOrWhiteSpace(type))
            {
                status.Text = "No provider drivers are registered.";
                return;
            }

            var name = nameBox.Text?.Trim();
            var existing = registry.Configs.FirstOrDefault(
                c => string.Equals(c.Type, type, StringComparison.OrdinalIgnoreCase));

            if (existing is not null)
            {
                // the form is the only editor for these fields, so Add doubles as Save
                if (!string.IsNullOrWhiteSpace(name)) existing.Name = name;
                if (keyBox.Text is { Length: > 0 }) existing.ApiKey = keyBox.Text;
                if (UiKit.TryReadInt(concurrency.Text, out var cc) && cc > 0) existing.Concurrency = cc;
                existing.Enabled = existing.ApiKey is { Length: > 0 };

                Sync();
                Refresh();
                keyBox.Text = string.Empty;
                status.Text = existing.Enabled
                    ? $"{existing.Name} updated and enabled."
                    : $"{existing.Name} updated — add an API key to enable it.";
                return;
            }

            var config = new CaptchaProviderConfig
            {
                Type = type,
                Name = string.IsNullOrWhiteSpace(name) ? type : name,
                ApiKey = keyBox.Text,
                Concurrency = UiKit.TryReadInt(concurrency.Text, out var c2) && c2 > 0 ? c2 : 10,
                Enabled = keyBox.Text is { Length: > 0 },
                Priority = 0,
            };

            registry.AddConfig(config);
            Sync();
            Refresh();
            keyBox.Text = string.Empty;
            status.Text = config.Enabled
                ? $"{config.Name} added and enabled."
                : $"{config.Name} added — add an API key to enable it.";
        }

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("Enabled",
                enabledList,
                UiKit.Row("Reordered priority", UiKit.Buttons(
                    UiKit.Button("Up", () => Move(-1)),
                    UiKit.Button("Down", () => Move(1))))),
            UiKit.Section("Disabled", disabledList),
            UiKit.Section("Add a provider",
                UiKit.Row("Type", typeCombo),
                UiKit.Row("Name", nameBox),
                UiKit.Row("API key", keyBox),
                UiKit.Row("Concurrency", concurrency),
                UiKit.Buttons(
                    UiKit.Button("Add", () => Add.Execute(null)),
                    UiKit.Button("Edit", () => Edit.Execute(null)),
                    UiKit.Button("Fetch balance", () =>
                    {
                        var configured = registry.Configs.FirstOrDefault(c => c.ApiKey is { Length: > 0 });
                        if (configured is null) { status.Text = "No provider has an API key yet."; return; }
                        var driver = registry.Driver(configured.Type);
                        if (driver is null) { status.Text = "Unknown driver."; return; }

                        configured.IsFetchingBalance = true;
                        var balance = driver.GetBalanceAsync(services.Http, configured, default)
                            .GetAwaiter().GetResult();
                        configured.IsFetchingBalance = false;
                        configured.Balance = balance;
                        status.Text = balance is null
                            ? $"{configured.Name}: balance unavailable."
                            : $"{configured.Name}: {balance}";
                        Refresh();
                    }))),
            status));
    
        Add = new RelayCommand(AddProvider);
        Edit = new RelayCommand(() => {
                        // there is no separate edit sheet; the form above is the editor, so point
                        // at it instead of claiming a sheet opened
                        var picked = enabledList.SelectedIndex is var ei && ei >= 0 && ei < _enabled.Count
                            ? _enabled[ei]
                            : disabledList.SelectedIndex is var di && di >= 0 && di < _disabled.Count
                                ? _disabled[di]
                                : null;

                        if (picked is null)
                        {
                            nameBox.Focus();
                            status.Text = "Select a provider, or fill the form and press Add.";
                            return;
                        }

                        typeCombo.SelectedItem = picked.Type;
                        nameBox.Text = picked.Name;
                        concurrency.Text = picked.Concurrency.ToString();
                        keyBox.Focus();
                        status.Text = $"Editing {picked.Name}. Change the fields, then Add.";
                    });}
}

/// <summary>
/// Cloudflare solvers (Cybersole.Ui.Views.Settings.CloudflareSolversView). Same shape as the
/// captcha list but scoped to turnstile / cf_clearance producers.
/// </summary>
public sealed class CloudflareSolversView : UserControl
{
    /// <summary>Bound as <c>FetchBalance</c>; runs <c>FetchBalanceCore()</c>.</summary>
    public ICommand FetchBalance { get; }

    /// <summary>The only provider the live 5.18.32 Add Cloudflare Provider dialog offers.</summary>
    public static readonly IReadOnlyList<string> Providers = new[] { "uncaptcha.io" };

    private readonly AppServices _solverServices;

    // The form's four inputs, hoisted out of the layout tree so Add can read them (R187) and so the
    // bound Edit command can fill them without reaching into the visual tree.
    private TextBox? _nameBox;
    private ComboBox? _providerCombo;
    private TextBox? _keyBox;
    private TextBox? _concurrencyBox;
    private ListBox? _rows;
    private TextBlock? _status;

    /// <summary>
    /// Loads the selected provider into the form below for editing (bound as <c>Edit</c>).
    ///
    /// <para>
    /// Evidence: the original's CloudflareSolversView command table is <c>Reorder</c> / <c>Edit</c> /
    /// <c>FetchBalance</c> (<c>analysis/pe_strings.txt</c> 0x0351da5b, with the async
    /// <c>&lt;ExecuteFetchBalance&gt;d__15</c> state machine beside it). The replica has Add and Fetch
    /// balance but no edit path, which is exactly this gap. "Editing" here means the same thing it
    /// means on the captcha page: the form above <i>is</i> the editor, so Edit points at it rather
    /// than opening a second sheet the original may not have.
    /// </para>
    /// </summary>
    public ICommand Edit { get; }

    /// <summary>The <c>Edit</c> body: copies the selected row into the form and returns the sentence to print.</summary>
    public string EditSelected()
    {
        var settings = _solverServices.Config.Settings;
        var index = _rows?.SelectedIndex ?? -1;
        if (index < 0 || index >= settings.CloudflareSolvers.Count)
        {
            _nameBox?.Focus();
            return "Select a provider, or fill the form and press Add.";
        }

        var picked = settings.CloudflareSolvers[index];
        if (_providerCombo is not null) _providerCombo.SelectedItem = picked.Type;
        if (_nameBox is not null) _nameBox.Text = picked.Name;
        if (_keyBox is not null) _keyBox.Text = picked.ApiKey ?? string.Empty;
        if (_concurrencyBox is not null) _concurrencyBox.Text = picked.Concurrency.ToString();
        _keyBox?.Focus();
        return $"Editing {picked.Name}. Change the fields, then Add.";
    }

    /// <summary>
    /// Asks the configured Cloudflare solver for its balance and stores it (bound as <c>FetchBalance</c>). Returns the line
    /// the page prints, so the button and any keybind report the same thing.
    /// </summary>
    public string FetchBalanceCore()
    {
        var settings = _solverServices.Config.Settings;
        var cf = settings.CloudflareSolvers.FirstOrDefault();
        if (cf is null) return "No Cloudflare provider configured.";
        if (cf.ApiKey is not { Length: > 0 })
            return $"{cf.Name}: no API key, so no balance to ask for.";

        var driver = _solverServices.Captcha.Registry.Driver("uncaptcha");
        cf.Balance = driver?.GetBalanceAsync(_solverServices.Http, new CaptchaProviderConfig
        {
            Type = "uncaptcha",
            Name = cf.Name,
            ApiKey = cf.ApiKey,
        }, default).GetAwaiter().GetResult() is { } balance ? (double)balance : 0;

        _solverServices.Config.Save();
        return $"{cf.Name}: {cf.Balance}";
    }

    /// <summary>
    /// R487: the original binds <c>Add</c> as a **property** on this view. The action already existed as a
    /// 46-line button lambda; the body is moved verbatim (only re-indented) so its two pre-existing
    /// encoding remnants are not disturbed.
    /// </summary>
    public ICommand Add { get; }

    public CloudflareSolversView(AppServices services)
    {
        FetchBalance = new RelayCommand(() => FetchBalanceCore());
        _solverServices = services;
        Edit = new RelayCommand(() => { if (_status is not null) _status.Text = EditSelected(); });
        var s = services.Config.Settings;
        var status = UiKit.Status();
        var rows = new ListBox { Height = 170 };
        // R400: the page now says its own line — "Add a Cloudflare provider to get started"
        // (Settings.CloudflareSolvers.EmptySubtitle) instead of the proxies sentence it used to print.
        var empty = EmptyView.For("cloudflare");

        // the form's fields, hoisted out of the layout tree so Add can read them
        var nameBox = UiKit.Text(watermark: "uncaptcha.io");
        var providerCombo = UiKit.Combo(Providers);
        var keyBox = UiKit.Text(password: true);
        var concurrencyBox = UiKit.Number(5);

        // R432: the bound Edit command fills these, so it needs handles to them; the local names stay
        // because the layout below reads better with them.
        _nameBox = nameBox;
        _providerCombo = providerCombo;
        _keyBox = keyBox;
        _concurrencyBox = concurrencyBox;
        _rows = rows;
        _status = status;

        void Refresh()
        {
            var items = s.CloudflareSolvers
                .Select(c => $"{c.Name}  ({c.Type})  concurrency={c.Concurrency}  " +
                             $"key={(c.ApiKey is { Length: > 0 } ? "set" : "missing")}")
                .ToList();

            rows.ItemsSource = items;
            rows.IsVisible = items.Count > 0;
            empty.IsVisible = items.Count == 0;
        }

        Refresh();

        // Advice-type placeholder, same as Add Accounts on the Email page (round 110): the text
        // was right about where to go, so send the caret there instead of only saying it.
        var add = UiKit.Button("Add Provider", () =>
        {
            keyBox.Focus();
            status.Text = "Fill the name, provider and API key below, then press Add.";
        });

        Add = new RelayCommand(() =>
        {
            // This used to hard-code Providers[0] and concurrency 5, ignoring the
            // four fields right underneath — filling them in did nothing.
            var type = providerCombo.SelectedItem as string ?? Providers[0];
            var name = nameBox.Text?.Trim();

            s.CloudflareSolvers.Add(new CloudflareSolverConfig
            {
                Name = string.IsNullOrWhiteSpace(name) ? type : name,
                Type = type,
                ApiKey = keyBox.Text is { Length: > 0 } ? keyBox.Text : null,
                Concurrency = UiKit.TryReadInt(concurrencyBox.Text, out var cc) && cc > 0
                    ? cc
                    : 5,
            });

            services.Config.Save();
            Refresh();
            keyBox.Text = string.Empty;

            var added = s.CloudflareSolvers[^1];

            // R187: the task group's "Cloudflare solver" dropdown reads
            // _services.Captcha.Registry.Configs (TasksViews.cs:359), not
            // settings.CloudflareSolvers. A provider added here was therefore
            // invisible in the one place it gets chosen — the same shape as the
            // round-113 defect (edit one object, save another). Both lists move
            // together now.
            if (!services.Captcha.Registry.Configs.Any(c =>
                    string.Equals(c.Name, added.Name, StringComparison.Ordinal)))
            {
                services.Captcha.Registry.AddConfig(new CaptchaProviderConfig
                {
                    Type = "cfsolver",
                    Name = added.Name,
                    ApiKey = added.ApiKey,
                    Concurrency = added.Concurrency,
                    Enabled = added.ApiKey is { Length: > 0 },
                });
                services.Config.Save();
            }

            status.Text = added.ApiKey is null
                ? $"{added.Name} added — set an API key to use it."
                : $"{added.Name} added.";
        });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                UiKit.Row("", add),
                rows,
                empty,
                UiKit.Row("Add Cloudflare provider",
                    UiKit.Buttons(
                        UiKit.Button("Add", () => Add.Execute(null)),
                        UiKit.Button("Fetch balance", () =>
                        {
                            status.Text = FetchBalanceCore();
                            Refresh();
                        }))),
                UiKit.Row("Name", nameBox),
                UiKit.Row("Provider", providerCombo),
                UiKit.Row("API Key", keyBox),
                UiKit.Row("Concurrency", concurrencyBox)),
            status));
    }
}

/// <summary>
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
    /// <summary>Bound as <c>Add</c>: the same command instance the "Add Size(s)" button carries.</summary>
    public ICommand Add { get; }

    /// <summary>Bound as <c>Clear</c>: the same command instance the "Clear Sizes" button carries.</summary>
    public ICommand Clear { get; }


    /// <summary>The page's one sortable column.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name" };

    /// <summary>Words the modal prints before a search.</summary>
    public const string DialogTitle = "Add Custom Sizes";
    public const string DialogPrompt = "Enter product URL";
    public static readonly string DialogEmptyTitle = EmptyView.Headline;
    public const string DialogEmptySubtitle = "Search a valid product URL";

    /// <summary>The page's count caption. The live page says "Custom Sizes" even at zero.</summary>
    public static string CountCaption(int count) =>
        count + (count == 1 ? " Custom Size" : " Custom Sizes");

    /// <summary>The size presets on the page (bound as <c>Rows</c>).</summary>
    public IReadOnlyList<string> Rows => _sizeRows;

    /// <summary>
    /// Removes the preset at <paramref name="index"/> and saves (bound as <c>Delete</c>). <c>View</c> is bound too but
    /// its meaning is unknown, so it is listed in docs/BINDING_BACKLOG.md instead of being guessed.
    /// </summary>
    public bool Delete(int index)
    {
        if (index < 0 || index >= _sizeRows.Count) return false;

        _sizeRows.RemoveAt(index);
        _services.Config.Save();
        return true;
    }

    private readonly AppServices _services = null!;
    private readonly List<string> _sizeRows = new();

    public CustomSizesView(AppServices services)
    {
        _services = services;
        var status = UiKit.Status();
        var sizes = new List<string>(services.Config.Settings.CustomSizes ?? new List<string>());
        _sizeRows.AddRange(sizes);

        var count = new TextBlock { Opacity = 0.7, VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        var header = new Grid { ColumnDefinitions = new ColumnDefinitions("34,1*") };
        var body = new StackPanel();
        var empty = EmptyPane(EmptyView.Headline, "Add some size presets to get started");

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
            // R83: same story as Add Preset — SizeCreatorView already existed.
            var modal = new Modals.SizeCreatorView(services, Refresh);
            if (TopLevel.GetTopLevel(this) is Window owner) modal.ShowDialog(owner);
            else modal.Show();
        });
        Add = addSizes.Command!;

        var clearSizes = UiKit.Button("Clear Sizes", () =>
        {
            sizes.Clear();
            Persist();
            Refresh();
            status.Text = "All size presets cleared.";
        });
        Clear = clearSizes.Command!;

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

/// <summary>
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
    /// <summary>Bound as <c>Add</c>: the same command the "Add Preset" button carries.</summary>
    public ICommand Add { get; }


    /// <summary>The three sortable columns, in the live page's order.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name", "URL", "Currency" };

    /// <summary>The modal's one field caption.</summary>
    public const string DialogPrompt = "Enter store URL";

    /// <summary>The modal's title.</summary>
    public const string DialogTitle = "Add Custom Store";

    /// <summary>The page's count caption. The live page says "Presets" even at zero.</summary>
    public static string CountCaption(int count) => count + (count == 1 ? " Preset" : " Presets");

    /// <summary>The presets on the page (bound as <c>Rows</c>).</summary>
    public IReadOnlyList<CustomStore> Rows => _storeRows;

    /// <summary>
    /// Removes the preset at <paramref name="index"/> and saves (bound as <c>Delete</c>). False when the index is out of
    /// range. <c>View</c> is bound too but its meaning is unknown, so it is listed in docs/BINDING_BACKLOG.md instead.
    /// </summary>
    public bool Delete(int index)
    {
        if (index < 0 || index >= _storeRows.Count) return false;

        _storeRows.RemoveAt(index);
        _services.Config.Save();
        return true;
    }

    private readonly AppServices _services = null!;
    private readonly List<CustomStore> _storeRows = new();

    /// <summary>Bound as <c>Clear</c>: the same command instance the "Clear Presets" button carries.</summary>
    public ICommand Clear { get; }

    public CustomStoresView(AppServices services)
    {
        _services = services;
        var status = UiKit.Status();
        var stores = services.Config.Settings.CustomStores ?? new List<CustomStore>();
        _storeRows.AddRange(stores);

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
                    Text = EmptyView.Headline,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = FontWeight.SemiBold,
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
            // R83: this used to be a hand-built Window here, while
            // Views/Settings/Modals/StoreCreatorView.cs already existed — two copies of one dialog.
            // The modal is the single implementation now, and it carries the live wording.
            var modal = new Modals.StoreCreatorView(services, Refresh);
            if (TopLevel.GetTopLevel(this) is Window owner) modal.ShowDialog(owner);
            else modal.Show();
        });
        Add = addPreset.Command!;

        var clear = UiKit.Button("Clear Presets", () =>
        {
            stores.Clear();
            Persist();
            Refresh();
            status.Text = "All presets cleared.";
        });
            Clear = clear.Command!;

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

/// <summary>
/// Data (Cybersole.Ui.Views.Settings.DataView) — Backup / Restore / Export / Reset plus the
/// log retention knobs.
/// </summary>
public sealed class DataView : UserControl
{

    // ------------------------------------------------ copy from the image's locale (R414)
    //
    // The Data.* strings that had no counterpart, verbatim (same table shape as the other pages). Export's failure
    // pair was already here from R349; these are the rest of the family.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["BackupMessage"] = "Successfully backed up all data.",   // Data.Backup.Message
        ["BackupTitle"] = "Backup Success",   // Data.Backup.Title
        ["ExportSuccessMessage"] = "Successfully exported data.",   // Data.Export.Success.Message
        ["ImportFailMessage"] = "Failed to import data.",   // Data.Import.Fail.Message
        ["ImportFailTitle"] = "Import Fail",   // Data.Import.Fail.Title
        ["ImportSuccessMessage"] = "Successfully imported data.",   // Data.Import.Success.Message
        ["ImportSuccessTitle"] = "Import Success",   // Data.Import.Success.Title
        ["ImportUnsupportedTitle"] = "File Unsupported",   // Data.Import.Unsupported.Title
        ["ImportUnsupportedJson"] = "This file type is unsupported. Please import a JSON file.",   // Data.Import.UnsupportedJson
        ["ImportUnsupportedJsonCsv"] = "This file type is unsupported. Please import a JSON / CSV file.",   // Data.Import.UnsupportedJsonCsv
        ["ResetMessage"] = "This will clear all data.",   // Data.Reset.Message
        ["RestoreFailedTitle"] = "Restore Failed",   // Data.Restore.Failed.Title
                ["RestoreFailedMessage"] = "Failed to restore data from the backup file. Make sure the selected file is in the correct format and hasn't been corrupted.",   // Data.Restore.Failed.Message
        ["RestoreSuccessMessage"] = "Successfully restored all data from backup.",   // Data.Restore.Success.Message
        ["RestoreSuccessTitle"] = "Restored Successfully",   // Data.Restore.Success.Title
    };

    /// <summary>One of the image's data-page strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    /// <summary>Choices the live "Select data" dropdown offers when exporting.</summary>
    public static readonly IReadOnlyList<string> ExportKinds = new[]
    {
        "All data", "Tasks", "Profiles", "Proxies", "Accounts", "Settings",
    };

    /// <summary>Labels the live "Backup Interval" dropdown offers.</summary>
    public static readonly IReadOnlyList<string> BackupIntervals = new[]
    {
        "30 minutes", "1 hour", "3 hours", "6 hours", "12 hours", "24 hours",
    };

    /// <summary>Labels the live "Maximum Retention Time" dropdown offers.</summary>
    public static readonly IReadOnlyList<string> RetentionTimes = new[]
    {
        "1 day", "3 days", "1 week", "2 weeks", "1 month",
    };

    // ------------------------------------------------ bound members (R240)
    //
    // The original binds DataProviders / ViewBackups on DataView (analysis/xaml_bindings.json): the first is the
    // export/import kind list, the second is the backup list the page shows.

    private readonly List<string> _backupNames = new();

    /// <summary>The page's status line, kept so the bound commands can report the same sentence the buttons do.</summary>
    private TextBlock? _status;

    // R349: the export toast copy, verbatim from the locale (Data.Export.*).
    public const string ExportSuccessTitle = "Export Success";
    public const string ExportFailTitle = "Export Fail";
    public const string ExportFailMessage = "Failed to export data.";

    /// <summary>
    /// The confirmation the original shows before a restore overwrites live state
    /// (<c>Data.Restore.Confirm.Message</c>). R627: the restore handler used to back up and restore in one step with
    /// no question, even though its own comment already said restoring overwrites live state.
    /// </summary>
    public const string RestoreConfirmMessage =
        "Restoring data from a backup file will override all existing data. This action cannot be undone!";

    /// <summary>The data kinds this page can export/import (bound as <c>DataProviders</c>).</summary>
    public IReadOnlyList<string> DataProviders => ExportKinds;

    /// <summary>The backup files currently listed, newest first (bound as <c>ViewBackups</c>).</summary>
    public IReadOnlyList<string> ViewBackups => _backupNames;

    /// <summary>
    /// Opens the log folder (bound as <c>ViewLogs</c>).
    ///
    /// <para>
    /// Evidence: the original's DataView command table is <c>Reset</c> / <c>ViewLogs</c> /
    /// <c>ViewBackups</c> / <c>Restore</c> (<c>analysis/pe_strings.txt</c> 0x0351dcc5), plus the
    /// <c>Export</c> / <c>Backup</c> descriptors in <c>docs/xaml_bindings.json</c>. The replica has
    /// carried the "View Logs" button since R75 but exposed no member by that name, which is the whole
    /// of this gap: same action, no binding.
    /// </para>
    /// </summary>
    public ICommand ViewLogs { get; }

    /// <summary>The <c>ViewLogs</c> body: opens <c>AppPaths.LogsDir</c> in the shell and returns the sentence to print.</summary>
    public string OpenLogs()
    {
        var dir = Cybersole.Core.Store.AppPaths.LogsDir;
        try
        {
            System.IO.Directory.CreateDirectory(dir);
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = dir,
                UseShellExecute = true,
            });
            return "Opened " + dir;
        }
        catch (Exception ex)
        {
            return "Cannot open the log folder: " + ex.Message;
        }
    }

    /// <summary>Re-reads the backup directory into <see cref="ViewBackups"/>.</summary>
    public IReadOnlyList<string> RefreshBackups()
    {
        _backupNames.Clear();
        var dir = new DirectoryInfo(Cybersole.Core.Store.AppPaths.BackupsDir);
        if (dir.Exists)
            _backupNames.AddRange(dir.GetFiles("*.cyb")
                .OrderByDescending(f => f.LastWriteTime)
                .Select(f => $"{f.Name}  ({f.Length / 1024} KB)"));

        return _backupNames;
    }

    /// <summary>
    /// R486: the original binds <c>Restore</c> as a **property** on this view. The action already existed as
    /// a button lambda (back up, restore, report); the body moves verbatim into a command.
    /// </summary>
    public ICommand Restore { get; }

    /// <summary>Bound as <c>Reset</c>: the same command instance the Reset button carries.</summary>
    public ICommand Reset { get; }

    public DataView(AppServices services)
    {
        var s = services.Config.Settings;
        var status = UiKit.Status();
        _status = status;
        ViewLogs = new RelayCommand(() => { if (_status is not null) _status.Text = OpenLogs(); });
        var backups = new ListBox { Height = 130 };

        void Refresh()
        {
            try
            {
                var dir = new DirectoryInfo(Cybersole.Core.Store.AppPaths.BackupsDir);
                backups.ItemsSource = dir.Exists
                    ? dir.GetFiles("*.cyb").OrderByDescending(f => f.LastWriteTime)
                        .Select(f => $"{f.Name}  ({f.Length / 1024} KB)").ToList()
                    : new List<string>();
            }
            catch (Exception ex)
            {
                status.Text = "Cannot read backups: " + ex.Message;
            }
        }

        Refresh();

        var exportKind = UiKit.Combo(ExportKinds);

        // "Export" and "Reset" used to write a sentence to the status bar and nothing else.
        // Round 117 gave them teeth: Export writes a real file through the platform picker,
        // Reset clears the chosen slice and saves.
        var export = UiKit.Button("Export", async () =>
        {
            var top = TopLevel.GetTopLevel(this);
            if (top?.StorageProvider is not { CanSave: true } sp)
            {
                status.Text = "This platform has no save dialog.";
                return;
            }

            var kind = exportKind.SelectedItem as string ?? "All data";
            var picked = await sp.SaveFilePickerAsync(new FilePickerSaveOptions
            {
                Title = "Export " + kind,
                SuggestedFileName = $"Cybersole {kind} {DateTime.Now:yyyy-MM-dd}.json",
                FileTypeChoices = new[]
                {
                    new FilePickerFileType("JSON") { Patterns = new[] { "*.json" } },
                },
            }).ConfigureAwait(true);

            if (picked is null) { status.Text = "Export cancelled."; return; }

            try
            {
                services.Config.Export(picked.Path.LocalPath, kind);
                var size = new FileInfo(picked.Path.LocalPath).Length;
                status.Text = $"{DataView.ExportSuccessTitle}: {kind} ({size / 1024} KB)";
            }
            catch (Exception ex)
            {
                // R349: the image carries a title and a message for this failure (Data.Export.Fail.Title / .Message),
                // so the status line leads with the title it prints there instead of a home-grown sentence.
                status.Text = $"{DataView.ExportFailTitle} — {DataView.ExportFailMessage} ({ex.Message})";
            }
        });

        var reset = UiKit.Button("Reset", async () =>
        {
            var kind = exportKind.SelectedItem as string ?? "All data";

            // Reset is destructive and has no undo, so it asks. The old handler claimed the reset
            // happened without asking and without doing it.
            var owner = TopLevel.GetTopLevel(this) as Window;
            if (owner is not null)
            {
                var confirm = new Window
                {
                    Title = "Reset " + kind,
                    Width = 420,
                    Height = 170,
                    WindowStartupLocation = WindowStartupLocation.CenterOwner,
                };
                var yes = false;
                confirm.Content = UiKit.Form(
                    UiKit.Section("Reset " + kind,
                        UiKit.Caption($"This clears {kind.ToLowerInvariant()} and cannot be undone. " +
                                      "Take a backup first if you are unsure."),
                        UiKit.Buttons(
                            UiKit.Button("Reset", () => { yes = true; confirm.Close(); }),
                            UiKit.Button("Cancel", () => confirm.Close()))));
                await confirm.ShowDialog(owner).ConfigureAwait(true);
                if (!yes) { status.Text = "Reset cancelled."; return; }
            }

            switch (kind)
            {
                case "Tasks": services.Config.TaskGroups.Clear(); break;
                case "Profiles": services.Config.BillingGroups.Clear(); break;
                case "Proxies": services.Config.ProxyGroups.Clear(); break;
                case "Accounts": services.Config.Accounts.AccountGroups.Clear(); break;
                case "Settings": services.Config.ResetSettings(); break;
                default: status.Text = "Pick one data set to reset — All data is too broad."; return;
            }

            services.Config.Save();
            Refresh();
            status.Text = $"{kind} reset.";
        });
        Reset = reset.Command!;

        // The drop zone was a Border with a TextBlock: it said "drag and drop to import, or click
        // to select file" and had no handler at all. Now it actually accepts both.
        async Task ImportFromFileAsync(string path)
        {
            if (!path.EndsWith(".json", StringComparison.OrdinalIgnoreCase)
                && !path.EndsWith(".cyb", StringComparison.OrdinalIgnoreCase))
            {
                status.Text = "Only .json exports and .cyb backups can be imported.";
                return;
            }

            if (path.EndsWith(".cyb", StringComparison.OrdinalIgnoreCase))
            {
                status.Text = services.Config.Restore(path)
                    ? "Restored from " + Path.GetFileName(path)
                    : "That backup could not be read.";
                Refresh();
                return;
            }

            status.Text = "JSON imports are not wired yet — use Restore for .cyb backups.";
            await Task.CompletedTask;
        }

        var dropZone = new Border
        {
            BorderBrush = Brushes.DimGray,
            BorderThickness = new Thickness(1),
            CornerRadius = new CornerRadius(6),
            Padding = new Thickness(24),
            Margin = new Thickness(0, 6),
            Child = new TextBlock
            {
                Text = "Drag and drop to import, or click to select file",
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                Opacity = 0.7,
            },
        };
        dropZone.PointerPressed += async (_, _) =>
        {
            var top = TopLevel.GetTopLevel(this);
            if (top?.StorageProvider is not { CanOpen: true } sp)
            {
                status.Text = "This platform has no file dialog.";
                return;
            }

            var files = await sp.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = "Import a backup",
                AllowMultiple = false,
                FileTypeFilter = new[]
                {
                    new FilePickerFileType("Cybersole backup") { Patterns = new[] { "*.cyb" } },
                    new FilePickerFileType("JSON") { Patterns = new[] { "*.json" } },
                },
            }).ConfigureAwait(true);

            if (files.Count > 0) await ImportFromFileAsync(files[0].Path.LocalPath);
        };
        DragDrop.SetAllowDrop(dropZone, true);
        dropZone.AddHandler(DragDrop.DropEvent, async (_, e) =>
        {
            var dropped = e.Data.GetFiles()?.FirstOrDefault();
            if (dropped is not null) await ImportFromFileAsync(dropped.Path.LocalPath);
        });

        var interval = UiKit.Combo(BackupIntervals, IndexOfInterval(s.BackupInterval));
        var maxBackups = UiKit.Number(s.MaxBackups);
        var maxSize = UiKit.Number(s.MaxLogSize);
        var retention = UiKit.Combo(RetentionTimes, IndexOfRetention(s.MaxLogRetention));

        Restore = new RelayCommand(async () =>
        {
            if (backups.SelectedIndex < 0) { status.Text = "Select a backup first."; return; }

            var row = backups.SelectedItem?.ToString() ?? string.Empty;
            // the list row reads "Name  (N KB)"; the file name is everything before that
            var file = row.Split("  (")[0];
            var full = System.IO.Path.Combine(
                Cybersole.Core.Store.AppPaths.BackupsDir, file);

            // R627: restore overwrites live state and has no undo, so it asks first -- the contract carries
            // Data.Restore.Confirm.Message for exactly this step. Before this the handler backed up and restored in
            // one go: it knew the danger (its own comment said so) and never asked.
            if (TopLevel.GetTopLevel(this) is Window owner)
            {
                var yes = false;
                var confirm = new Window
                {
                    Title = "Restore",
                    Width = 460,
                    Height = 190,
                    WindowStartupLocation = WindowStartupLocation.CenterOwner,
                };
                confirm.Content = UiKit.Form(
                    UiKit.Section("Restore",
                        UiKit.Caption(RestoreConfirmMessage),
                        UiKit.Buttons(
                            UiKit.Button("Restore", () => { yes = true; confirm.Close(); }),
                            UiKit.Button("Cancel", () => confirm.Close()))));
                await confirm.ShowDialog(owner).ConfigureAwait(true);
                if (!yes) { status.Text = "Restore cancelled."; return; }
            }

            // Back up first, then report whether the file actually parsed.
            services.Config.Backup();
            if (services.Config.Restore(full))
            {
                Refresh();
                status.Text = $"Restored {file}. Your previous state was backed up first.";
            }
            else
            {
                status.Text = $"{file} could not be restored.";
            }
        });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                UiKit.Row("Import, export and backup data",
                    UiKit.Buttons(exportKind, export, reset)),
                dropZone,
                UiKit.Row("Backup", UiKit.Buttons(
                    UiKit.Button("Backup Now", () =>
                    {
                        services.Config.Backup();
                        Refresh();
                        status.Text = "Backup written.";
                    }),
                    UiKit.Button("View Backups", () =>
                    {
                        // this at least selects something instead of only printing a count
                        if (backups.ItemCount == 0)
                        {
                            status.Text = "No backups yet — press Backup Now first.";
                            return;
                        }
                        backups.SelectedIndex = 0;
                        status.Text = $"{backups.ItemCount} backup(s) on disk; newest selected.";
                    }))),
                UiKit.Row("Restore from backup", UiKit.Button("Restore", () => Restore.Execute(null))),
                backups,
                UiKit.Row("Max backups", maxBackups),
                UiKit.Row("Backup Interval", interval),
                new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 8) },
                UiKit.Row("Logs", UiKit.Button("View Logs", () => status.Text = OpenLogs())),
                UiKit.Row("Max file size", UiKit.Row("mb", maxSize)),
                UiKit.Row("Maximum Retention Time", retention),
                UiKit.Buttons(UiKit.Button("Save", () =>
                {
                    if (UiKit.TryReadInt(maxBackups.Text, out var mb)) s.MaxBackups = mb;
                    if (UiKit.TryReadInt(maxSize.Text, out var ms)) s.MaxLogSize = ms;
                    s.BackupInterval = IntervalOf(interval.SelectedIndex);
                    s.MaxLogRetention = RetentionOf(retention.SelectedIndex);
                    services.Config.Save();
                    status.Text = "Saved.";
                }))),
            status));
    }

    private static int IndexOfInterval(TimeSpan value) => value.TotalMinutes switch
    {
        <= 30 => 0,
        <= 60 => 1,
        <= 180 => 2,
        <= 360 => 3,
        <= 720 => 4,
        _ => 5,
    };

    private static TimeSpan IntervalOf(int index) => index switch
    {
        0 => TimeSpan.FromMinutes(30),
        1 => TimeSpan.FromHours(1),
        2 => TimeSpan.FromHours(3),
        3 => TimeSpan.FromHours(6),
        4 => TimeSpan.FromHours(12),
        _ => TimeSpan.FromHours(24),
    };

    private static int IndexOfRetention(TimeSpan value) => value.TotalDays switch
    {
        <= 1 => 0,
        <= 3 => 1,
        <= 7 => 2,
        <= 14 => 3,
        _ => 4,
    };

    private static TimeSpan RetentionOf(int index) => index switch
    {
        0 => TimeSpan.FromDays(1),
        1 => TimeSpan.FromDays(3),
        2 => TimeSpan.FromDays(7),
        3 => TimeSpan.FromDays(14),
        _ => TimeSpan.FromDays(30),
    };
}

/// <summary>Webhooks (Cybersole.Ui.Views.Settings.WebhookView).</summary>
public sealed class WebhookView : UserControl
{
    /// <summary>Bound as <c>Delete</c>; the button with that label runs this command.</summary>
    public ICommand Delete { get; }


    /// <summary>
    /// The extra payload fields a webhook can carry, in the order the locale lists them (R341).
    ///
    /// <para>
    /// Evidence is five dictionary keys in the image: <c>Settings.Webhook.ExtraFields</c> plus
    /// <c>Settings.Webhook.Extra.Email</c>, <c>.Price</c>, <c>.CheckoutProxy</c> and <c>.ProxyGroup</c>, whose English
    /// values are the labels below. The "New Webhook" modal does <b>not</b> show them (R340 walked all three submit
    /// states with Platform = Discord and no extra row appeared), so where they are toggled is still unknown — this
    /// constant records what exists, not where it goes.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> ExtraFieldChoices = new[]
    {
        "Email", "Price", "Checkout Proxy", "Proxy Group",
    };

    /// <summary>
    /// R485: the original binds <c>Add</c> as a **property** on this view. The action already existed as a
    /// button lambda over the local inputs, so it stays a lambda and only becomes a command.
    /// </summary>
    public ICommand Add { get; }

    public WebhookView(AppServices services)
    {
        var status = UiKit.Status();
        var rows = new ListBox { Height = 160 };

        var all = services.Config.Settings.Webhooks;

        void Refresh() => rows.ItemsSource = all
            .Select(w => $"{w.Name ?? "(unnamed)"} — {w.Url}  enabled={w.Enabled}")
            .ToList();

        Refresh();

        var name = UiKit.Text(watermark: "Checkouts");
        var url = UiKit.Text(watermark: "https://discord.com/api/webhooks/…");
        var targetGroup = UiKit.Combo(services.Config.TaskGroups.Select(g => g.Name).ToList());

        Add = new RelayCommand(() =>
        {
            if (string.IsNullOrWhiteSpace(url.Text)) { status.Text = "URL required."; return; }
            var gi = Math.Clamp(targetGroup.SelectedIndex, 0,
                Math.Max(0, services.Config.TaskGroups.Count - 1));
            services.Config.Settings.Webhooks.Add(new Webhook
            {
                Name = name.Text ?? "Webhook",
                Url = url.Text!,
            });

            services.Config.Save();
            Refresh();
            status.Text = "Webhook added.";
        });

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                rows,
                UiKit.Row("Name", name),
                UiKit.Row("URL", url),
                UiKit.Row("Attach to group", targetGroup),
                UiKit.Buttons(
                    UiKit.Button("Add", () => Add.Execute(null)),
                    UiKit.Button("Delete", () => Delete.Execute(null)),
                    UiKit.Button("Test", async () =>
                    {
                        if (rows.SelectedIndex < 0) { status.Text = "Select a webhook."; return; }
                        var target = all[rows.SelectedIndex];

                        // "Test queued for {url}" used to be the whole handler — a status line
                        // that claimed work it never did. Now it actually posts.
                        status.Text = $"Testing {target.Url}…";
                        try
                        {
                            var payload = "{\"content\":\"Cybersole webhook test\","
                                        + "\"username\":\"Cybersole\"}";
                            var res = await services.Http.PostJsonAsync(target.Url, payload)
                                .ConfigureAwait(true);

                            status.Text = res is null
                                ? "Test failed: no response"
                                : $"Test: HTTP {res.StatusCode} ({res.BodyBytes} B)";
                        }
                        catch (Exception ex)
                        {
                            status.Text = "Test failed: " + ex.Message;
                        }
                    }))),
            UiKit.Section("Events", UiKit.Caption(
                "Checkouts · Declines · PayPal · Payment requests · Smart actions")),
            status));
    
        Delete = new RelayCommand(() => {
                        if (rows.SelectedIndex < 0) return;
                        var target = all[rows.SelectedIndex];
                        services.Config.Settings.Webhooks.Remove(target);
                        
                        services.Config.Save();
                        Refresh();
                        status.Text = "Deleted.";
                    });}
}

/// <summary>
/// Advanced (Cybersole.Ui.Views.Settings.KeyBindsView sibling — the recovered
/// <c>Settings.Nav.Advanced</c> page).
/// </summary>
public sealed class AdvancedView : UserControl
{
    public AdvancedView(AppServices services)
    {
        var s = services.Config.Settings;
        var status = UiKit.Status();

        var beta = UiKit.Check("Beta updates", s.BetaUpdates);
        var pinGroups = UiKit.Check("Pin task groups", s.PinGroups);
        var profileOrder = UiKit.Combo(Enum.GetNames<ProfileGroupOrder>(), (int)s.ProfileGroupOrder);
        var proxyOrder = UiKit.Combo(Enum.GetNames<ProxyGroupOrder>(), (int)s.ProxyGroupOrder);
        var taskOrder = UiKit.Combo(Enum.GetNames<TaskGroupOrder>(), (int)s.TaskGroupOrder);

        var stores = services.Stores.Modules.Count;
        var flows = typeof(StoreFlow).Assembly.GetTypes()
            .Count(t => t.IsSubclassOf(typeof(StoreFlow)) && !t.IsAbstract);

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("Updates",
                UiKit.Row("Beta channel", beta)),
            UiKit.Section("Ordering",
                UiKit.Row("Task groups", taskOrder),
                UiKit.Row("Proxy groups", proxyOrder),
                UiKit.Row("Profile groups", profileOrder),
                UiKit.Row("Pin groups", pinGroups)),
            UiKit.Section("Diagnostics",
                UiKit.Caption($"Registered stores: {stores}"),
                UiKit.Caption($"Step flows: {flows}"),
                UiKit.Caption($"Captcha drivers: {services.Captcha.Registry.Drivers.Count}"),
                UiKit.Caption($"Actions: {Cybersole.Stores.Actions.StepActionRegistry.CreateDefault().All.Count}")),
            UiKit.Buttons(UiKit.Button("Save", () =>
            {
                s.BetaUpdates = beta.IsChecked == true;
                s.PinGroups = pinGroups.IsChecked == true;
                s.TaskGroupOrder = (TaskGroupOrder)Math.Max(0, taskOrder.SelectedIndex);
                s.ProxyGroupOrder = (ProxyGroupOrder)Math.Max(0, proxyOrder.SelectedIndex);
                s.ProfileGroupOrder = (ProfileGroupOrder)Math.Max(0, profileOrder.SelectedIndex);
                services.Config.Save();
                status.Text = "Saved.";
            })),
            status));
    }
}

/// <summary>
/// Need help (Cybersole.Ui.Views.Settings.HelpView).
///
/// <para>
/// R81 drove the live page top to bottom. It is not a row of buttons — it is the error index:
/// </para>
///
/// <code>
/// Get Help
/// Take a look at common errors or contact support
/// [                Open help center                    ]
/// [ Search errors                                     ]
/// [General] Connection Error
/// Target website unreachable or your proxies are currently not working.
/// ... thirteen entries, scrollable ...
/// </code>
///
/// <para>
/// The replica had three buttons and a comment saying <i>"there is no error index to search"</i>
/// — while <c>ErrorCatalog.All</c> had been holding all thirteen entries, word for word, since an
/// earlier round. The catalogue existed and nothing rendered it: the "built but never bound"
/// orphan, on the one page whose whole job is to show it.
/// </para>
/// </summary>
public sealed class HelpView : UserControl
{
    public const string CommunityUrl = "https://cybersole.io";

    // Round 118: this pointed at https://cybersole.io/api/apisecuretoken, which is an API
    // endpoint, not documentation. "Open center" opened nothing at all; the URL was wrong too.
    public const string DocsUrl = "https://cybersole.io/docs";

    /// <summary>The page's two controls, as the live build words them.</summary>
    public const string OpenCenterLabel = "Open help center";
    public const string SearchLabel = "Search errors";

    /// <summary>
    /// The entries whose title or detail contains <paramref name="query"/>, in catalogue order.
    /// An empty query returns everything — the live page starts with the whole index on screen.
    /// </summary>
    /// <summary>
    /// Opens one of the help links in the default browser (bound as <c>OpenUrl</c>, R346). The two URLs the page offers
    /// are <see cref="CommunityUrl"/> and <see cref="DocsUrl"/>; this is the operation the binding table names.
    /// </summary>
    public static bool OpenUrl(string url)
    {
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = url,
                UseShellExecute = true,
            });
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    public static IReadOnlyList<Cybersole.Stores.Flows.ErrorCatalog.Entry> Filter(string? query)
    {
        var all = Cybersole.Stores.Flows.ErrorCatalog.All;
        if (string.IsNullOrWhiteSpace(query)) return all;

        var needle = query.Trim();
        return all
            .Where(e => e.Title.Contains(needle, StringComparison.OrdinalIgnoreCase)
                        || e.Detail.Contains(needle, StringComparison.OrdinalIgnoreCase))
            .ToList();
    }

    public HelpView(AppServices services)
    {
        var status = UiKit.Status();

        void Open(string url) => OpenUrl(url);

        var openCenter = new Button
        {
            Content = OpenCenterLabel,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
            HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            Padding = new Thickness(12, 8),
        };
        openCenter.Click += (_, _) => Open(DocsUrl);

        var search = UiKit.Text();
        search.Watermark = SearchLabel;

        var list = new StackPanel { Spacing = 14 };
        var empty = new TextBlock
        {
            Text = "No matching errors",
            Opacity = 0.6,
            Margin = new Thickness(0, 20),
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
        };

        void Render()
        {
            var matches = Filter(search.Text);
            list.Children.Clear();

            foreach (var entry in matches)
            {
                list.Children.Add(new StackPanel
                {
                    Spacing = 4,
                    Children =
                    {
                        new TextBlock { Text = entry.Title },
                        new TextBlock
                        {
                            Text = entry.Detail,
                            Opacity = 0.65,
                            TextWrapping = TextWrapping.Wrap,
                        },
                    },
                });
            }

            empty.IsVisible = matches.Count == 0;
            status.Text = matches.Count == Cybersole.Stores.Flows.ErrorCatalog.All.Count
                ? $"{matches.Count} error entries."
                : $"{matches.Count} of {Cybersole.Stores.Flows.ErrorCatalog.All.Count} entries match.";
        }

        search.TextChanged += (_, _) => Render();
        Render();

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(openCenter, search, list, empty),
            status));
    }
}
