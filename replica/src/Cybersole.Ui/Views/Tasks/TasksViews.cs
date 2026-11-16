using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Services;
using System.Windows.Input;

namespace Cybersole.Ui.Views.Tasks;

/// <summary>
/// Task creator (Cybersole.Ui.Views.Tasks.TaskCreatorView) — three tabs matching the
/// recovered <c>TaskCreator.Tab.Setup</c> / <c>.Cart</c> / <c>.Advanced</c> keys.
/// </summary>
public sealed class TaskCreatorView : UserControl
{

    // ------------------------------------------------ copy from the image's locale (R412)
    //
    // The TaskCreator.* strings that had no counterpart, verbatim. Same table shape as the other two pages.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["CreateTask"] = "Create Task",   // TaskCreator.Button.CreateTask
        ["CreateTasksFormat"] = "Create {0} Tasks",   // TaskCreator.Button.CreateTasksFormat
        ["SaveTask"] = "Save Task",   // TaskCreator.Button.SaveTask
        ["SaveTasksFormat"] = "Save {0} Tasks",   // TaskCreator.Button.SaveTasksFormat
        ["MonitorInput"] = "Monitor Input",   // TaskCreator.MonitorInput
        ["MonitorInputDefault"] = "Enter input",   // TaskCreator.MonitorInput.Default
        ["MonitorInputFormat"] = "Enter {0}",   // TaskCreator.MonitorInput.Format
        ["MonitorInputMultiple"] = "Multiple inputs",   // TaskCreator.MonitorInput.Multiple
        ["MultiCart"] = "Multi Cart active",   // TaskCreator.MultiCart
        ["ProfileMultiple"] = "Multiple profiles",   // TaskCreator.Profile.Multiple
        ["ProfileSelect"] = "Select profile",   // TaskCreator.Profile.Select
        ["ProxiesMultiple"] = "Multiple proxy groups",   // TaskCreator.Proxies.Multiple
        ["ProxiesSelect"] = "Select proxy group",   // TaskCreator.Proxies.Select
        ["SizeMultiple"] = "Multiple sizes",   // TaskCreator.Size.Multiple
        ["SizeSelect"] = "Select sizes",   // TaskCreator.Size.Select
        ["StartTimeMultiple"] = "Multiple start times",   // TaskCreator.StartTime.Multiple
        ["StartTimeSet"] = "Set start time",   // TaskCreator.StartTime.Set
        ["StoreMultiple"] = "Multiple stores",   // TaskCreator.Store.Multiple
        ["StoreSelect"] = "Select store",   // TaskCreator.Store.Select
    };

    /// <summary>One of the image's task-creator strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    private readonly AppServices _services;
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    /// <summary>Bound as <c>Create</c>: the same command the "Create task" button carries.</summary>
    public ICommand Create { get; }

    public TaskCreatorView(AppServices services, BotTask? existing = null)
    {
        Close = new RelayCommand(() => CloseCore());

        _services = services;

        var tabs = new TabControl { Height = 520 };
        _tabs = tabs;   // R233: ShowCartView reads the selected tab
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "Setup", Content = BuildSetup(existing) },
            new TabItem { Header = "Cart", Content = BuildCart(existing) },
            new TabItem { Header = "Advanced", Content = BuildAdvanced(existing) },
        };

        var createButton = UiKit.Button("Create task", () => Save(existing));
        Create = createButton.Command!;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title(existing is null ? "New task" : $"Edit task — {existing.Name}"),
                tabs,
                UiKit.Buttons(
                    createButton,
                    // there is no bulk sheet yet; the extra-URL control lives in this same editor,
                    // so say that rather than describing a multi-line box that does not exist
                    UiKit.Button("Create tasks", () =>
                        Status("Use + Add product for more URLs in one task."))),
                _status,
            },
        };
    }

    private void Status(string text) => _status.Text = text;

    // ── Setup ─────────────────────────────────────────────────────────────────
    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    private Control BuildSetup(BotTask? existing)
    {
        var name = UiKit.Text(existing?.Name, watermark: "Task name");
        var url = UiKit.Text(existing?.Product.Url, watermark: "https://store.example/products/item");
        var store = UiKit.Combo(_services.Stores.Modules.Select(m => m.Name).ToList(),
            IndexOf(_services.Stores.Modules.Select(m => m.Name).ToList(), existing?.Store));
        var sizes = UiKit.Text(string.Join(", ", existing?.Product.Sizes ?? new List<string>()),
            watermark: "9, 10, 10.5");

        _nameBox = name;
        _urlBox = url;
        _storeBox = store;
        _sizesBox = sizes;
        var quantity = UiKit.Number(1);
        var profiles = UiKit.Combo(new[] { "Auto", "Explicit" });
        var proxies = UiKit.Combo(new[] { "Auto", "Explicit" });
        var accounts = UiKit.Combo(_services.Config.Accounts.AccountGroups
            .SelectMany(g => g.Accounts)
            .Select(a => string.IsNullOrWhiteSpace(a.Email) ? a.Id : a.Email)
            .DefaultIfEmpty("(none)").ToList());

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Name", name),
            UiKit.Row("Product URL", url),
            UiKit.Row("Store", store),
            UiKit.Row("Sizes", sizes),
            UiKit.Row("Quantity", quantity),
            UiKit.Row("Profile", profiles),
            UiKit.Row("Proxies", proxies),
            UiKit.Row("Account", accounts)));
    }

    // ── price check (R241) ───────────────────────────────────────────────────
    //
    // The original's input model binds PriceCheckVisible / TogglePriceCheck. The creator already had the
    // "Price check" checkbox; these two give it the vocabulary the original uses.

    /// <summary>Whether the price bounds apply — true while the price check switch is on (bound as <c>PriceCheckVisible</c>).</summary>
    public bool PriceCheckVisible => _priceCheckBox?.IsChecked == true;

    /// <summary>Flips the price check switch and returns the new state (bound as <c>TogglePriceCheck</c>).</summary>
    public bool TogglePriceCheck()
    {
        if (_priceCheckBox is null) return false;
        _priceCheckBox.IsChecked = !(_priceCheckBox.IsChecked == true);
        return _priceCheckBox.IsChecked == true;
    }

    // ── bound members (R233) ─────────────────────────────────────────────────
    //
    // The original binds these on TaskCreatorMainView (analysis/xaml_bindings.json):
    //   ProfileGroupItems, ProfileItems, ShowCartView, SizeItems
    // The three lists are what the setup/cart tabs offer; ShowCartView is which tab is showing.

    private TabControl? _tabs;

    /// <summary>The size chips on offer (bound as <c>SizeItems</c>).</summary>
    public IReadOnlyList<string> SizeItems =>
        Cybersole.Core.Models.SizePalette.Build(_services.Config.Settings.CustomSizes);

    /// <summary>
    /// Every profile the user has, flattened across the profile groups (bound as <c>ProfileItems</c>).
    /// The profile groups are the Billing page's left rail — <c>Config.BillingGroups</c>.
    /// </summary>
    public IReadOnlyList<Profile> ProfileItems =>
        _services.Config.BillingGroups.SelectMany(g => g.Profiles).ToList();

    /// <summary>The profile groups (bound as <c>ProfileGroupItems</c>).</summary>
    public IReadOnlyList<BillingGroup> ProfileGroupItems => _services.Config.BillingGroups;

    /// <summary>True while the Cart tab is the selected one (bound as <c>ShowCartView</c>).</summary>
    public bool ShowCartView
    {
        get => _tabs?.SelectedIndex == 1;
        set
        {
            if (_tabs is null || !value) return;
            _tabs.SelectedIndex = 1;
        }
    }

    /// <summary>
    /// Steps the "Quantity (per profile)" field up by one (bound as <c>Plus</c> on the input model). R263: the original
    /// shows −/+ steppers beside that field (measured R242); the replica had a plain number box.
    /// </summary>
    public int Plus() => StepQuantity(+1);

    /// <summary>Steps the quantity down by one, never below 1 (bound as <c>Minus</c>).</summary>
    public int Minus() => StepQuantity(-1);

    /// <summary>The quantity the field currently holds.</summary>
    public int Quantity => ReadQuantity();

    private int ReadQuantity() =>
        _quantityPerProfileBox is not null && UiKit.TryReadInt(_quantityPerProfileBox.Text, out var q) ? q : 1;

    private int StepQuantity(int delta)
    {
        if (_quantityPerProfileBox is null) return 1;

        var next = Math.Max(1, ReadQuantity() + delta);
        _quantityPerProfileBox.Text = next.ToString(System.Globalization.CultureInfo.InvariantCulture);
        return next;
    }

    // ── Cart ──────────────────────────────────────────────────────────────────
    private Control BuildCart(BotTask? existing)
    {
        var multiCart = UiKit.Check("Multi-cart", false);
        var quantityPerProfile = UiKit.Number(1);
        var autoQuantity = UiKit.Check("Auto quantity", false);
        ToolTip.SetTip(autoQuantity, "Automatically set the quantity to the maximum the store allows for the product, replacing the quantity you entered.");
        var checkoutDelay = UiKit.Number(existing?.CheckoutDelay ?? 0);

        _multiCartBox = multiCart;
        _quantityPerProfileBox = quantityPerProfile;

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Multi cart", multiCart),
            UiKit.Row("Quantity per profile", quantityPerProfile),
            UiKit.Row("Auto quantity", autoQuantity),
            UiKit.Row("Checkout delay (ms)", checkoutDelay)));
    }

    // ── Advanced ──────────────────────────────────────────────────────────────
    private Control BuildAdvanced(BotTask? existing)
    {
        var s = _services.Config.Settings;
        var monitor = UiKit.Number(existing?.MonitorDelay ?? s.MonitorDelay);
        var retry = UiKit.Number(existing?.RetryDelay ?? s.RetryDelay);
        var timeout = UiKit.Number(existing?.Timeout ?? s.Timeout);
        var monitorMode = UiKit.Check("Monitor only", existing?.MonitorMode ?? false);
        var scheduled = UiKit.Text(existing?.StartTime?.ToString("HH:mm:ss"), watermark: "HH:mm:ss");
        var priceCheck = UiKit.Check("Price check", existing?.Product.PriceCheck ?? false);

        _monitorDelayBox = monitor;
        _retryDelayBox = retry;
        _timeoutBox = timeout;
        _monitorOnlyBox = monitorMode;
        _priceCheckBox = priceCheck;
        _startTimeBox = scheduled;

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Monitor delay (ms)", monitor),
            UiKit.Row("Retry delay (ms)", retry),
            UiKit.Row("Timeout (s)", timeout),
            UiKit.Row("Monitor only", monitorMode),
            UiKit.Row("Scheduled start", scheduled),
            UiKit.RowCheck("Price check", false)));
    }

    // ── selection state for the cartesian build ───────────────────────────────
    private readonly List<string> _selectedSizes = new();
    private readonly List<string> _selectedProfiles = new();
    private readonly List<string> _selectedProxyGroups = new();
    private TextBox? _nameBox;
    private TextBox? _urlBox;
    private TextBox? _sizesBox;
    private TextBox? _quantityPerProfileBox;
    private ComboBox? _storeBox;
    private CheckBox? _multiCartBox;
    private CheckBox? _monitorOnlyBox;
    private CheckBox? _priceCheckBox;
    private TextBox? _monitorDelayBox;
    private TextBox? _retryDelayBox;
    private TextBox? _timeoutBox;
    private TextBox? _startTimeBox;

    /// <summary>How many tasks the current form would create (TaskCreator.Quantity).</summary>
    public int PendingCount() => TaskCombinationBuilder.Count(BuildRequest());

    private TaskCombinationRequest BuildRequest()
    {
        var sizes = (_sizesBox?.Text ?? string.Empty)
            .Split(',', StringSplitOptions.RemoveEmptyEntries)
            .Select(s => s.Trim())
            .Where(s => s.Length > 0)
            .ToList();

        var profiles = _selectedProfiles.Count > 0
            ? _selectedProfiles
            : _services.Config.BillingGroups
                .SelectMany(g => g.Profiles)
                .Select(p => p.Id)
                .ToList();

        return new TaskCombinationRequest
        {
            Store = _storeBox?.SelectedItem as string ?? string.Empty,
            Url = _urlBox?.Text,
            NameTemplate = "{store} {size} {profile} {index}",
            Sizes = sizes,
            Profiles = profiles,
            ProxyGroupIds = _selectedProxyGroups.Count > 0
                ? _selectedProxyGroups
                : _services.Config.ProxyGroups.Select(g => g.Id).ToList(),
            QuantityPerProfile = UiKit.TryReadInt(_quantityPerProfileBox?.Text, out var q) ? q : 1,
            MultiCart = _multiCartBox?.IsChecked == true,
            StartTime = DateTime.TryParse(_startTimeBox?.Text, out var st) ? st : null,
            MonitorDelay = UiKit.TryReadInt(_monitorDelayBox?.Text, out var md) ? md : null,
            RetryDelay = UiKit.TryReadInt(_retryDelayBox?.Text, out var rd) ? rd : null,
            Timeout = UiKit.TryReadInt(_timeoutBox?.Text, out var to) ? to : null,
            MonitorMode = _monitorOnlyBox?.IsChecked == true,
            PriceCheck = _priceCheckBox?.IsChecked == true,
        };
    }

    private void Save(BotTask? existing)
    {
        try
        {
            var group = _services.Config.TaskGroups.FirstOrDefault();
            if (group is null)
            {
                Status("Create a task group first.");
                return;
            }

            if (existing is not null)
            {
                existing.Name = string.IsNullOrWhiteSpace(_nameBox?.Text) ? existing.Name : _nameBox!.Text!;
                existing.Product.Url = _urlBox?.Text;
                _services.Config.Save();
                Status("Task saved.");
                return;
            }

            var request = BuildRequest();
            if (string.IsNullOrWhiteSpace(request.Store))
            {
                Status("Pick a store first.");
                return;
            }

            var built = TaskCombinationBuilder.Build(request);
            foreach (var task in built) group.Tasks.Add(task);

            _services.Config.Save();
            Status($"Created {built.Count} task(s) from {request.Sizes.Count} size(s) × " +
                   $"{Math.Max(1, request.Profiles.Count)} profile(s).");
        }
        catch (Exception ex)
        {
            Status(ex.Message);
        }
    }

    private static int IndexOf(IReadOnlyList<string> items, string? value) =>
        value is null ? 0 : Math.Max(0, items.ToList().FindIndex(
            x => string.Equals(x, value, StringComparison.OrdinalIgnoreCase)));
}

/// <summary>
/// Task group editor (Cybersole.Ui.Views.Tasks.Modals.TaskGroupView) — six tabs matching
/// the recovered <c>TaskGroup.Tab.*</c> keys plus the Manual page.
/// </summary>
public sealed class TaskGroupView : UserControl
{
    /// <summary>Bound as <c>Delete</c>; the button with that label runs this command.</summary>
    public ICommand Delete { get; }


    private readonly AppServices _services;
    private readonly TextBlock _status = UiKit.Status();
    private readonly TaskGroup _group;

    /// <summary>
    /// The Cloudflare solvers this group can pick from (bound as <c>CloudflareSolvers</c>). The dialog fills its combo
    /// from this list, so the property and the control cannot disagree.
    /// </summary>
    public IReadOnlyList<string> CloudflareSolvers =>
        _services.Captcha.Registry.Configs.Select(c => c.Name).DefaultIfEmpty("(none)").ToList();

    /// <summary>The group this dialog is editing — the draft (bound as <c>Draft</c>).</summary>
    // ------------------------------------------------ copy from the image's locale (R396)
    //
    // The dialog's own labels and the link tooltip, verbatim (TaskGroup.* in the string table). The Delays tab had
    // "Monitor delay" / "Error delay" in lower case, which is not what the image shows.

    /// <summary>"Captcha Solving Source" — the captcha tab's first label.</summary>
    public const string CaptchaSourceLabel = "Captcha Solving Source";

    /// <summary>"Select source" — the captcha source combo's placeholder.</summary>
    public const string CaptchaSourceSelect = "Select source";

    /// <summary>"Cloudflare Solver" — the captcha tab's second label.</summary>
    public const string CloudflareSolverLabel = "Cloudflare Solver";

    /// <summary>"Monitor Delay" — the delays tab.</summary>
    public const string MonitorDelayLabel = "Monitor Delay";

    /// <summary>"Error Delay" — the delays tab's second field.</summary>
    public const string ErrorDelayLabel = "Error Delay";

    /// <summary>The link toggle's tooltip.</summary>
    public const string LinkTooltip = "When toggled, both monitor and retry delays will stay the same";

    /// <summary><c>TaskGroup.CloudflareSolver.Tooltip</c> (verbatim). Not yet wired to a control — see R548.</summary>
    public const string CloudflareSolverTooltip = "Solves this group's Cloudflare challenges. Add third party providers under Settings > Cloudflare Providers. A task without a proxy, or with a local one (e.g. Charles on 127.0.0.1), still has its challenges solved in-bot.";

    /// <summary><c>TaskGroup.Tab.Delays.Tooltip</c> (verbatim). Not yet wired to a control — see R548.</summary>
    public const string DelaysTabTooltip = "Group specific delays.\n\nIf none are set, global delays will be used, you can adjust these in settings.";

    /// <summary><c>TaskGroup.WebhookFilter.Tooltip</c> (verbatim). Not yet wired to a control — see R548.</summary>
    public const string WebhookFilterTooltip = "Once configured, notifications are delivered exclusively to the specified webhooks. If no webhooks are selected, notifications are sent to all available webhooks by default.";

    /// <summary>"Resetting at" — the limits tab.</summary>
    public const string ResettingAtLabel = "Resetting at";

    /// <summary>"Total Checkout Limit" — the limits tab's first field.</summary>
    public const string TotalCheckoutLimitLabel = "Total Checkout Limit";

    /// <summary>"Webhook Filter" — the notifications tab.</summary>
    public const string WebhookFilterLabel = "Webhook Filter";

    /// <summary>"Select webhook(s)" — the filter combo's placeholder.</summary>
    public const string WebhookFilterSelect = "Select webhook(s)";

    public TaskGroup Draft => _group;

    /// <summary>
    /// R480: the original binds <c>Save</c> as a **property** on this dialog. The action already existed —
    /// `Save()` was passed to the button as a method group — so the method is renamed `SaveCore` to free the
    /// bound name, and the behaviour is untouched.
    /// </summary>
    public ICommand Save { get; }

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    public TaskGroupView(AppServices services, TaskGroup? group = null)
    {
        Close = new RelayCommand(() => CloseCore());

        Save = new RelayCommand(SaveCore);
        _services = services;
        _group = group ?? new TaskGroup();

        // R352: the locale names exactly four tabs — TaskGroup.Tab.{Delays,Limits,Captcha,Notifications} — with no
        // "General" and no "Manual". The old Manual tab misread TaskGroup.TimeSpan.Manual, which is one of the "Reset
        // limits after" options; PeriodStart belongs to the Limits tab (its tooltip lives there) and the group's
        // Pinned/Order are not part of this dialog at all (Pinned is TaskView.PinGroups, Order is
        // Settings.TaskGroupOrder), so those three controls are gone rather than relocated.
        var tabs = new TabControl { Height = 480 };
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "Delays", Content = BuildDelays() },
            new TabItem { Header = "Limits", Content = BuildLimits() },
            new TabItem { Header = "Captcha", Content = BuildCaptcha() },
            new TabItem { Header = "Notifications", Content = BuildNotifications() },
        };

        // R351: the live dialog prints "Group Name" as its own field above the tab strip.
        var groupName = UiKit.Text(_group.Name, watermark: "Group Name");
        groupName.TextChanged += (_, _) => _group.Name = groupName.Text ?? _group.Name;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                new TextBlock { Text = "Group Settings", FontSize = 16, FontWeight = Avalonia.Media.FontWeight.SemiBold },
                UiKit.Row("Group Name", groupName),
                tabs,
                UiKit.Buttons(
                    UiKit.Button("Delete", () => Delete.Execute(null)),
                    UiKit.Button("Save", () => Save.Execute(null))),
                _status,
            },
        };
    
        Delete = new RelayCommand(() => DeleteGroup());}

    private Control BuildGeneral()
    {
        var pinned = UiKit.Check("Pinned", _group.Pinned);
        var order = UiKit.Number(_group.Order ?? 0);

        pinned.IsCheckedChanged += (_, _) => _group.Pinned = pinned.IsChecked == true;
        order.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(order.Text, out var v)) _group.Order = v;
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Pinned", pinned),
            UiKit.Row("Order", order)));
    }

    private Control BuildDelays()
    {
        var monitor = UiKit.Number(_group.MonitorDelay);
        var retry = UiKit.Number(_group.RetryDelay);
        var error = UiKit.Number(_group.ErrorDelay);
        var timeout = UiKit.Number(_group.Timeout);
        var linked = UiKit.Check("Link monitor and retry", _group.LinkedDelays);

        // R53: "Reset limits after" is a duration choice, not a typed TimeSpan. The original's
        // options are the TaskGroup.TimeSpan.* locale keys.
        var spanValues = Enum.GetValues<TimeSpans>();
        // R66: index 0 is "(none)". Without it a null UsageExpiry displayed the first enum value.
        var spanLabels = new List<string> { "(none)" };
        spanLabels.AddRange(spanValues.Select(t => t.ToString()));
        var span = UiKit.Combo(spanLabels,
            _group.UsageExpiry is null ? 0 : Array.IndexOf(spanValues, _group.UsageExpiry.Value) + 1,
            i => _group.UsageExpiry = i <= 0 ? null : spanValues[Math.Clamp(i - 1, 0, spanValues.Length - 1)]);

        monitor.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(monitor.Text, out var v)) _group.MonitorDelay = v;
        };
        retry.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(retry.Text, out var v)) _group.RetryDelay = v;
        };
        error.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(error.Text, out var v)) _group.ErrorDelay = v;
        };
        timeout.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(timeout.Text, out var v)) _group.Timeout = v;
        };
        linked.IsCheckedChanged += (_, _) => _group.LinkedDelays = linked.IsChecked == true;

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row(MonitorDelayLabel, monitor),
            UiKit.Row(ErrorDelayLabel, retry),
            UiKit.Row("Retry Delay", error),
            UiKit.Row("Timeout (s)", timeout),
            UiKit.RowCheck("Linked delays", _group.LinkedDelays)));
    }

    private Control BuildLimits()
    {
        var checkoutLimit = UiKit.Number(_group.CheckoutLimit);
        var profileLimit = UiKit.Number(_group.ProfileLimit);

        // R53: "Reset limits after" lives here, beside the two limits it resets, not on the
        // delays tab. Its value is TaskGroup.UsageExpiry (a Cybersole.TimeSpans), which used to
        // be a separate ResetLimitsAfter TimeSpan — the same concept stored twice under two
        // names, and only one of them in the original.
        var limitSpanValues = Enum.GetValues<TimeSpans>();
        var limitSpanLabels = new List<string> { "(none)" };
        limitSpanLabels.AddRange(limitSpanValues.Select(t => t.ToString()));
        var resetAfter = UiKit.Combo(limitSpanLabels,
            _group.UsageExpiry is null ? 0 : Array.IndexOf(limitSpanValues, _group.UsageExpiry.Value) + 1,
            i => _group.UsageExpiry = i <= 0 ? null : limitSpanValues[Math.Clamp(i - 1, 0, limitSpanValues.Length - 1)]);

        checkoutLimit.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(checkoutLimit.Text, out var v)) _group.CheckoutLimit = v;
        };
        profileLimit.TextChanged += (_, _) =>
        {
            if (UiKit.TryReadInt(profileLimit.Text, out var v)) _group.ProfileLimit = v;
        };

        // R352: the period-start editor lives here, not on a tab of its own — the locale keeps its tooltip in this panel
        // ("Period starts when you first start a task") and TaskGroup.TimeSpan.Manual is one of the options above.
        var periodStart = UiKit.Text(_group.PeriodStart?.ToString("u"), watermark: "2026-01-01 00:00:00");
        periodStart.TextChanged += (_, _) =>
        {
            if (DateTime.TryParse(periodStart.Text, out var periodValue)) _group.PeriodStart = periodValue;
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row(TotalCheckoutLimitLabel, checkoutLimit),
            UiKit.Row("Checkout limit per profile", profileLimit),
            UiKit.Row("Reset limits after", resetAfter),
            UiKit.Row("Period start", periodStart),
            UiKit.Caption("Counters roll over automatically once the reset window elapses.")));
    }

    private Control BuildCaptcha()
    {
        var source = UiKit.Combo(Enum.GetNames<CaptchaSource>(), (int)_group.CaptchaSource);
        var solver = UiKit.Combo(CloudflareSolvers);

        source.SelectionChanged += (_, _) =>
            _group.CaptchaSource = (CaptchaSource)Math.Max(0, source.SelectedIndex);
        solver.SelectionChanged += (_, _) =>
        {
            var index = solver.SelectedIndex;
            if (index >= 0 && index < _services.Captcha.Registry.Configs.Count)
                _group.CloudflareSolver = _services.Captcha.Registry.Configs[index].Name;
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row(CaptchaSourceLabel, source),
            UiKit.Row(CloudflareSolverLabel, solver)));
    }

    private Control BuildNotifications()
    {
        var filter = UiKit.Combo(new[] { "All", "Checkouts only", "Declines only", "None" },
            _group.WebhookFilter switch
            {
                "Checkouts only" => 1,
                "Declines only" => 2,
                "None" => 3,
                _ => 0,
            });

        filter.SelectionChanged += (_, _) =>
            _group.WebhookFilter = filter.SelectedIndex switch
            {
                1 => "Checkouts only",
                2 => "Declines only",
                3 => "None",
                _ => "All",
            };

        var hooks = new ListBox
        {
            Height = 140,
            ItemsSource = _group.Webhooks.Select(w => $"{w.Name ?? "(unnamed)"} — {w.Url}").ToList(),
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row(WebhookFilterLabel, filter),
            UiKit.Row("Webhooks", hooks),
            UiKit.Caption("Add webhooks under Settings → Webhooks.")));
    }

    private Control BuildManual()
    {
        // R53: this box edits when the period began, not how long it lasts. It used to write to
        // UsageExpiry, which is now a Cybersole.TimeSpans — the two were conflated because both
        // were DateTime?. NextReset is the derived boundary, so it never needs an editor.
        var manual = UiKit.Text(_group.PeriodStart?.ToString("u"), watermark: "2026-01-01 00:00:00");
        manual.TextChanged += (_, _) =>
        {
            if (DateTime.TryParse(manual.Text, out var v)) _group.PeriodStart = v;
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Period start", manual),
            UiKit.Caption("Leave empty to start the usage window at the first task run.")));
    }

    /// <summary>
    /// Closes the hosting dialog (bound as <c>Close</c>). False when this control is not inside a window, which is what a
    /// test that builds the view without a host sees.
    /// </summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    /// <summary>Removes this group from the configuration (bound as <c>Delete</c>). False when it was never saved.</summary>
    public bool DeleteGroup()
    {
        if (!_services.Config.TaskGroups.Remove(_group)) return false;

        _services.Config.Save();
        _status.Text = "Group deleted.";
        return true;
    }

    private void SaveCore()
    {
        try
        {
            if (!_services.Config.TaskGroups.Contains(_group))
                _services.Config.TaskGroups.Add(_group);

            _services.Config.Save();
            _status.Text = "Group saved.";
        }
        catch (Exception ex)
        {
            _status.Text = ex.Message;
        }
    }

    private void Reset()
    {
        _group.MonitorDelay = null;
        _group.RetryDelay = null;
        _group.ErrorDelay = null;
        _group.Timeout = null;
        _group.CheckoutLimit = null;
        _group.ProfileLimit = null;
        _status.Text = "Delays and limits reset.";
    }
}

/// <summary>Task details (Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView).</summary>
public sealed class TaskDetailsView : UserControl
{
    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    public TaskDetailsView(AppServices services, BotTask task)
    {
        Close = new RelayCommand(() => CloseCore());

        var s = services.Config.Settings;

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("Task",
                UiKit.Row("Name", new TextBlock { Text = task.Name }),
                UiKit.Row("Store", new TextBlock { Text = task.Store }),
                UiKit.Row("URL", new TextBlock { Text = task.Product.Url ?? "(none)" }),
                UiKit.Row("Product", new TextBlock { Text = task.Product.Name })),
            UiKit.Section("Timing",
                UiKit.Row("Monitor delay", new TextBlock { Text = $"{task.MonitorDelay ?? s.MonitorDelay} ms" }),
                UiKit.Row("Retry delay", new TextBlock { Text = $"{task.RetryDelay ?? s.RetryDelay} ms" }),
                UiKit.Row("Timeout", new TextBlock { Text = $"{task.Timeout ?? s.Timeout} s" }),
                UiKit.Row("Monitor mode", new TextBlock { Text = task.MonitorMode ? "monitor only" : "monitor + checkout" })),
            UiKit.Section("Binding",
                UiKit.Row("Profile", new TextBlock { Text = task.ProfileId ?? "(auto)" }),
                UiKit.Row("Account", new TextBlock { Text = task.AccountId ?? "(none)" }),
                UiKit.Row("Proxy group", new TextBlock { Text = task.ProxyGroupId ?? "(auto)" }),
                UiKit.Row("Price check", new TextBlock { Text = task.Product.PriceCheck ? "on" : "off" })),
            UiKit.Section("State",
                UiKit.Row("Status", new TextBlock { Text = task.State.ToString() }),
                UiKit.Row("Start time", new TextBlock { Text = task.StartTime?.ToString("u") ?? "(none)" }))));
    }
}

/// <summary>Task group summary (Cybersole.Ui.Views.Tasks.Modals.GroupSummary).</summary>
public sealed class GroupSummary : UserControl
{
    private readonly TaskGroup _summaryGroup;

    private readonly AppServices _services;

    /// <summary>Whether this summary exists to be edited rather than viewed (bound as <c>Edit</c>) — always true for a
    /// summary that already names a group.</summary>
    public bool Edit => _summaryGroup is not null;

    /// <summary>Bound as <c>Clone</c>; runs <c>CloneCore()</c>.</summary>
    public ICommand Clone { get; }

    /// <summary>Bound as <c>StartAll</c>; runs <c>StartAllCore()</c>.</summary>
    public ICommand StartAll { get; }

    /// <summary>Bound as <c>StopAll</c>; runs <c>StopAllCore()</c>.</summary>
    public ICommand StopAll { get; }


    /// <summary>
    /// Duplicates this group and its tasks (bound as <c>Clone</c>). The copy is named "&lt;name&gt; copy" and appended to the
    /// configuration; returns the new group.
    /// </summary>
    public TaskGroup CloneCore()
    {
        var copy = new TaskGroup
        {
            Name = _summaryGroup.Name + " copy",
            MonitorDelay = _summaryGroup.MonitorDelay,
            RetryDelay = _summaryGroup.RetryDelay,
            ErrorDelay = _summaryGroup.ErrorDelay,
            Timeout = _summaryGroup.Timeout,
            CheckoutLimit = _summaryGroup.CheckoutLimit,
            ProfileLimit = _summaryGroup.ProfileLimit,
            Pinned = _summaryGroup.Pinned,
        };

        foreach (var task in _summaryGroup.Tasks)
            copy.Tasks.Add(new BotTask
            {
                Name = task.Name,
                Store = task.Store,
                Product = task.Product,
                GroupId = copy.Id,
                MonitorDelay = task.MonitorDelay,
                RetryDelay = task.RetryDelay,
                Timeout = task.Timeout,
            });

        _services.Config.TaskGroups.Add(copy);
        _services.Config.Save();
        return copy;
    }

    /// <summary>Deletes this group from the configuration (bound as <c>Delete</c>). False when it was not there.</summary>
    private bool DeleteCore()
    {
        if (!_services.Config.TaskGroups.Remove(_summaryGroup)) return false;

        _services.Config.Save();
        return true;
    }

    /// <summary>Starts every task in this group (bound as <c>StartAll</c>). Returns how many were started.</summary>
    public int StartAllCore()
    {
        var tasks = _summaryGroup.Tasks.Where(t => !t.IsRunning).ToList();
        if (tasks.Count > 0) _services.Tasks.StartAll(tasks);
        return tasks.Count;
    }

    /// <summary>Stops every running task in this group (bound as <c>StopAll</c>). Returns how many were stopped.</summary>
    public int StopAllCore()
    {
        var tasks = _summaryGroup.Tasks.Where(t => t.IsRunning).ToList();
        _services.Tasks.StopAll(tasks.Select(task => task.Id));
        return tasks.Count;
    }

    /// <summary>Whether the group is pinned to the top of the picker (bound as <c>PinGroup</c>).</summary>
    public bool PinGroup
    {
        get => _summaryGroup.Pinned;
        set => _summaryGroup.Pinned = value;
    }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Delete</c>; behaviour unchanged (was a method).</summary>
    public ICommand Delete { get; }

    public GroupSummary(AppServices services, TaskGroup group)
    {
        Delete = new RelayCommand(() => DeleteCore());
        Clone = new RelayCommand(() => CloneCore());
        StartAll = new RelayCommand(() => StartAllCore());
        StopAll = new RelayCommand(() => StopAllCore());

        _services = services;
        _summaryGroup = group;
        var running = group.Tasks.Count(t => t.IsRunning);
        var idle = group.Tasks.Count - running;

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section(group.Name,
                UiKit.Row("Tasks", new TextBlock { Text = group.Tasks.Count.ToString() }),
                UiKit.Row("Running", new TextBlock { Text = running.ToString() }),
                UiKit.Row("Idle", new TextBlock { Text = idle.ToString() }),
                UiKit.Row("Checkout limit", new TextBlock { Text = group.CheckoutLimit?.ToString() ?? "unlimited" }),
                UiKit.Row("Profile limit", new TextBlock { Text = group.ProfileLimit?.ToString() ?? "unlimited" })),
            UiKit.Section("Delays",
                UiKit.Row("Monitor", new TextBlock { Text = $"{group.MonitorDelay ?? services.Config.Settings.MonitorDelay} ms" }),
                UiKit.Row("Retry", new TextBlock { Text = $"{group.RetryDelay ?? services.Config.Settings.RetryDelay} ms" }),
                UiKit.Row("Error", new TextBlock { Text = $"{group.ErrorDelay ?? 0} ms" }),
                UiKit.Row("Timeout", new TextBlock { Text = $"{group.Timeout ?? services.Config.Settings.Timeout} s" }))));
    }
}

/// <summary>Task group list (Cybersole.Ui.Views.Tasks.Modals.TaskGroupListView).</summary>
public sealed class TaskGroupListView : UserControl
{
    /// <summary>The groups this list shows (bound as <c>Groups</c>).</summary>
    public IReadOnlyList<TaskGroup> Groups => _services.Config.TaskGroups;

    private readonly AppServices _services;
    private readonly ListBox _list = new() { Height = 320 };
    private readonly TextBlock _status = UiKit.Status();

    public TaskGroupListView(AppServices services)
    {
        _services = services;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Task groups"),
                _list,
                UiKit.Buttons(
                    UiKit.Button("New group", () =>
                    {
                        _services.Config.TaskGroups.Add(new TaskGroup
                        {
                            Name = $"Group {_services.Config.TaskGroups.Count + 1}",
                        });
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Group created.";
                    }),
                    UiKit.Button("Delete", () =>
                    {
                        if (_list.SelectedIndex < 0) return;
                        _services.Config.TaskGroups.RemoveAt(_list.SelectedIndex);
                        if (_services.Config.TaskGroups.Count == 0)
                            _services.Config.TaskGroups.Add(new TaskGroup { Name = "Group 1" });
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Group deleted.";
                    }),
                    UiKit.Button("Pin", () =>
                    {
                        if (_list.SelectedIndex < 0) return;
                        var g = _services.Config.TaskGroups[_list.SelectedIndex];
                        g.Pinned = !g.Pinned;
                        _services.Config.Save();
                        Refresh();
                        _status.Text = g.Pinned ? "Pinned." : "Unpinned.";
                    }),
                    UiKit.Button("Clone", () =>
                    {
                        if (_list.SelectedIndex < 0) return;

                        // R60: TaskGroups.Context.CloneFormat ("Clone {0}"). The clone copies the
                        // group's configuration — delays, limits, captcha source, shipping rate —
                        // and its tasks, but starts with a fresh Id and no counters. Copying
                        // TotalCheckouts/TotalDeclines would make a new group look like it had
                        // already run; NextReset is derived, so it follows PeriodStart rather than
                        // being copied.
                        var source = _services.Config.TaskGroups[_list.SelectedIndex];
                        var clone = new TaskGroup
                        {
                            Name = $"{source.Name} (copy)",
                            Order = source.Order,
                            UsageExpiry = source.UsageExpiry,
                            PeriodStart = null,
                            CheckoutLimit = source.CheckoutLimit,
                            ProfileLimit = source.ProfileLimit,
                            MonitorDelay = source.MonitorDelay,
                            RetryDelay = source.RetryDelay,
                            Timeout = source.Timeout,
                            LinkedDelays = source.LinkedDelays,
                            Pinned = source.Pinned,
                            CaptchaSource = source.CaptchaSource,
                            CloudflareSolver = source.CloudflareSolver,
                            ShippingRate = source.ShippingRate,
                            WebhookFilter = source.WebhookFilter,
                            ErrorDelay = source.ErrorDelay,
                            ResetLimitsAfter = source.ResetLimitsAfter,
                            Webhooks = source.Webhooks.ToList(),
                        };
                        foreach (var task in source.Tasks) clone.Tasks.Add(task.Clone());

                        _services.Config.TaskGroups.Add(clone);
                        _services.Config.Save();
                        Refresh();
                        _status.Text = $"Cloned \"{source.Name}\" ({clone.Tasks.Count} task(s)).";
                    })),
                _status,
            },
        };

        Refresh();
    }

    public void Refresh() => _list.ItemsSource = _services.Config.TaskGroups
        .Select(g => $"{(g.Pinned ? "* " : "")}{g.Name}  ({g.Tasks.Count} tasks)")
        .ToList();
}

/// <summary>
