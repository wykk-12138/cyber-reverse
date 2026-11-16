using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Task editor (Cybersole.Ui.Views.Tasks.Modals.TaskDetailsView + CreateModel).
/// Creates a BotTask from a product URL and the configured groups.
/// </summary>
public sealed class TaskEditorWindow : Window
{
    private readonly AppServices _services;
    private readonly TextBox _name = new() { Watermark = "Task name" };
    private readonly TextBox _url = new() { Watermark = "https://store.example/products/item" };
    private readonly ComboBox _store = new();
    private readonly ComboBox _proxyGroup = new();
    private readonly ComboBox _profile = new();
    private readonly ComboBox _account = new();
    private readonly TextBox _sizes = new() { Watermark = "9, 10, 10.5" };
    private readonly TextBox _monitorDelay = new();
    private readonly TextBox _retryDelay = new();
    private readonly TextBox _timeout = new();

    // The original's task creator has these three on separate tabs: Scheduled Start and
    // Quantity (per profile) under Setup, Monitor Mode under Advanced. This window is one page,
    // so they sit with the other timing fields — but they exist, which they did not before
    // round 94. StartTime already had a field on BotTask and MonitorMode had a bool; only
    // Quantity had to be added.
    private readonly TextBox _startTime = new() { Watermark = "yyyy-MM-dd HH:mm (local), blank = now" };
    private readonly TextBox _quantity = new() { Text = "1" };
    private readonly ComboBox _monitorMode = new();

    // one TextBox per "Add product" row; Save() reads these into BotTask.ExtraProducts
    private readonly List<TextBox> _extraBoxes = new();
    private readonly StackPanel _extraHost = new() { Spacing = 4 };

    private readonly TextBlock _error = new() { Foreground = new SolidColorBrush(Color.Parse("#F85149")) };

    public TaskEditorWindow(AppServices services, BotTask? existing = null)
    {
        _services = services;
        Title = existing is null ? "New task" : $"Edit task — {existing.Name}";
        Width = 560;
        Height = 520;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        var stores = _services.Stores.Modules.Select(m => m.Name).ToList();
        _store.ItemsSource = stores;
        _store.SelectedIndex = 0;

        _proxyGroup.ItemsSource = _services.Config.ProxyGroups.Select(g => g.Name).ToList();
        _proxyGroup.SelectedIndex = 0;

        var profiles = _services.Config.BillingGroups.SelectMany(g => g.Profiles).Select(p => p.Name).ToList();
        _profile.ItemsSource = profiles;
        _profile.SelectedIndex = profiles.Count > 0 ? 0 : -1;

        var accounts = _services.Config.Accounts.AccountGroups.SelectMany(g => g.Accounts)
            .Select(a => string.IsNullOrWhiteSpace(a.Email) ? a.Id : a.Email)
            .ToList();
        _account.ItemsSource = accounts;
        _account.SelectedIndex = accounts.Count > 0 ? 0 : -1;

        _monitorDelay.Text = _services.Config.Settings.MonitorDelay.ToString();
        _retryDelay.Text = _services.Config.Settings.RetryDelay.ToString();
        _timeout.Text = _services.Config.Settings.Timeout.ToString();

        // the original offers "Per Task" here; the model keeps it as a bool, so the two options
        // map onto it directly rather than inventing a per-site third state
        _monitorMode.ItemsSource = new List<string> { "Per Task", "Per Site" };
        _monitorMode.SelectedIndex = 0;

        if (existing is not null)
        {
            _name.Text = existing.Name;
            _url.Text = existing.Product.Url;
            _sizes.Text = string.Join(", ", existing.Product.Sizes);
            _monitorDelay.Text = (existing.MonitorDelay ?? _services.Config.Settings.MonitorDelay).ToString();
            _retryDelay.Text = (existing.RetryDelay ?? _services.Config.Settings.RetryDelay).ToString();
            _timeout.Text = (existing.Timeout ?? _services.Config.Settings.Timeout).ToString();
            _quantity.Text = existing.Quantity.ToString();
            _monitorMode.SelectedIndex = existing.MonitorMode ? 1 : 0;
            if (existing.StartTime is { } st)
                _startTime.Text = st.ToLocalTime().ToString("yyyy-MM-dd HH:mm");

            // Round 97 could create extra products but not show them again: opening an existing
            // task left the "More products" block with only the + button, so the rows were
            // invisible and a Save would have written the field back empty.
            foreach (var extra in existing.ExtraProducts)
                AddExtraRow(extra.Url ?? string.Empty);

            var storeIndex = stores.FindIndex(s => string.Equals(s, existing.Store, StringComparison.OrdinalIgnoreCase));
            if (storeIndex >= 0) _store.SelectedIndex = storeIndex;

            if (existing.ProfileId is not null)
            {
                var profileIndex = _services.Config.BillingGroups.SelectMany(g => g.Profiles)
                    .Select((p, i) => (p, i)).FirstOrDefault(x => x.p.Id == existing.ProfileId).i;
                if (profileIndex >= 0 && profileIndex < profiles.Count) _profile.SelectedIndex = profileIndex;
            }

            if (existing.AccountId is not null)
            {
                var accountIndex = _services.Config.Accounts.AccountGroups.SelectMany(g => g.Accounts)
                    .Select((a, i) => (a, i)).FirstOrDefault(x => x.a.Id == existing.AccountId).i;
                if (accountIndex >= 0 && accountIndex < accounts.Count) _account.SelectedIndex = accountIndex;
            }
        }

        var create = new Button { Content = existing is null ? "Create" : "Save", Padding = new Thickness(16, 5) };
        create.Click += (_, _) => Submit(existing);

        var cancel = new Button { Content = "Cancel" };
        cancel.Click += (_, _) => Close();

        var grid = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("140,*"),
            RowDefinitions = new RowDefinitions("Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto,Auto"),
        };

        void Row(int i, string label, Control input)
        {
            var l = new TextBlock { Text = label, VerticalAlignment = VerticalAlignment.Center };
            Grid.SetRow(l, i); Grid.SetColumn(l, 0);
            Grid.SetRow(input, i); Grid.SetColumn(input, 1);
            grid.Children.Add(l);
            grid.Children.Add(input);
        }

        // settings.customSizes → one-click chips under the Sizes field
        var sizeChips = new WrapPanel();
        foreach (var size in Cybersole.Core.Models.SizePalette.Build(_services.Config.Settings.CustomSizes))
        {
            var chip = new Button
            {
                Content = size,
                Margin = new Thickness(0, 0, 4, 4),
                Padding = new Thickness(7, 1),
                FontSize = 11,
            };
            chip.Click += (_, _) =>
            {
                var current = ImportParser.ParseSizes(_sizes.Text).ToList();
                if (!current.Contains(size, StringComparer.OrdinalIgnoreCase)) current.Add(size);
                _sizes.Text = string.Join(", ", current);
            };
            sizeChips.Children.Add(chip);
        }

        Row(0, "Name", _name);
        Row(1, "Product URL", _url);

        // The original's Cart tab has an "Add Input" row, so one task carries several URLs.
        // BotTask.ExtraProducts and TaskEngine's round-robin landed in round 95; this is the
        // control that fills them. Kept as a StackPanel inside a single grid row because Row()
        // positions by explicit index — inserting N rows would renumber everything below.

        void AddExtraRow(string url = "")
        {
            var line = new DockPanel { LastChildFill = true };

            var box = new TextBox
            {
                Text = url,
                Watermark = "https://store.example/products/another",
                Margin = new Thickness(0, 0, 6, 0),
            };

            var remove = new Button { Content = "×", Width = 30, Padding = new Thickness(0) };
            remove.Click += (_, _) =>
            {
                _extraHost.Children.Remove(line);
                _extraBoxes.Remove(box);
            };

            DockPanel.SetDock(remove, Dock.Right);
            line.Children.Add(remove);
            line.Children.Add(box);

            _extraHost.Children.Add(line);
            _extraBoxes.Add(box);
        }

        var addExtra = new Button { Content = "+ Add product", HorizontalAlignment = HorizontalAlignment.Left };
        addExtra.Click += (_, _) => AddExtraRow();

        var extraBlock = new StackPanel { Spacing = 4 };
        extraBlock.Children.Add(_extraHost);
        extraBlock.Children.Add(addExtra);

        Row(2, "More products", extraBlock);
        Row(3, "Store", _store);
        Row(4, "Sizes", _sizes);
        Row(5, "Quick sizes", sizeChips);
        Row(6, "Proxy group", _proxyGroup);
        Row(7, "Profile", _profile);
        Row(8, "Account", _account);
        Row(9, "Monitor delay (ms)", _monitorDelay);
        Row(10, "Retry delay (ms)", _retryDelay);
        Row(11, "Timeout (s)", _timeout);
        Row(12, "Scheduled start", _startTime);
        Row(13, "Quantity (per profile)", _quantity);
        Row(14, "Monitor mode", _monitorMode);

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Margin = new Thickness(0, 12, 0, 0),
            Children = { cancel, create },
        };

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 6,
            Children = { grid, _error, buttons },
        };
    }

    private void Submit(BotTask? existing)
    {
        var url = _url.Text?.Trim();
        if (string.IsNullOrWhiteSpace(url) || !Uri.TryCreate(url, UriKind.Absolute, out var uri))
        {
            _error.Text = "A valid absolute product URL is required.";
            return;
        }

        if (_store.SelectedIndex < 0)
        {
            _error.Text = "Pick a store.";
            return;
        }

        var storeModule = _services.Stores.Modules[_store.SelectedIndex];
        var sizes = ImportParser.ParseSizes(_sizes.Text).ToList();

        var group = _services.Config.TaskGroups.FirstOrDefault() ?? new TaskGroup();
        if (!_services.Config.TaskGroups.Contains(group)) _services.Config.TaskGroups.Add(group);

        var task = existing ?? new BotTask();
        task.Name = string.IsNullOrWhiteSpace(_name.Text) ? $"Task {group.Tasks.Count + 1}" : _name.Text!.Trim();
        task.Store = storeModule.Id;
        task.Product.Url = url;
        task.Product.Name = task.Product.Name.Length > 0 ? task.Product.Name : storeModule.Name;
        task.Product.Sizes = sizes.Count > 0 ? sizes : new List<string> { "One Size" };
        task.GroupId = group.Id;
        task.ProxyGroupId = _services.Config.ProxyGroups.ElementAtOrDefault(Math.Max(0, _proxyGroup.SelectedIndex))?.Id;
        var profiles = _services.Config.BillingGroups.SelectMany(g => g.Profiles).ToList();
        task.ProfileId = _profile.SelectedIndex >= 0 && _profile.SelectedIndex < profiles.Count
            ? profiles[_profile.SelectedIndex].Id
            : null;
        var accountList = _services.Config.Accounts.AccountGroups.SelectMany(g => g.Accounts).ToList();
        task.AccountId = _account.SelectedIndex >= 0 && _account.SelectedIndex < accountList.Count
            ? accountList[_account.SelectedIndex].Id
            : null;
        task.MonitorDelay = int.TryParse(_monitorDelay.Text, out var md) ? md : null;
        task.RetryDelay = int.TryParse(_retryDelay.Text, out var rd) ? rd : null;
        task.Timeout = int.TryParse(_timeout.Text, out var to) ? to : null;
        task.Quantity = int.TryParse(_quantity.Text, out var qty) && qty > 0 ? qty : 1;
        task.MonitorMode = _monitorMode.SelectedIndex == 1;

        // blank rows are dropped rather than kept as empty products: an empty URL would make the
        // engine poll "" every other turn
        task.ExtraProducts.Clear();
        foreach (var box in _extraBoxes)
        {
            if (string.IsNullOrWhiteSpace(box.Text)) continue;
            task.ExtraProducts.Add(new Product
            {
                Url = box.Text.Trim(),
                Sizes = task.Product.Sizes.ToList(),
            });
        }

        // blank means "start now"; anything unparseable is an error the user has to fix rather
        // than a silent fallback to now, because a mistyped schedule that runs immediately is
        // worse than one that refuses
        task.StartTime = null;
        if (!string.IsNullOrWhiteSpace(_startTime.Text))
        {
            if (DateTime.TryParse(_startTime.Text, out var parsed))
                task.StartTime = parsed.Kind == DateTimeKind.Local
                    ? parsed.ToUniversalTime()
                    : DateTime.SpecifyKind(parsed, DateTimeKind.Local).ToUniversalTime();
            else
                _error.Text = $"Scheduled start '{_startTime.Text}' is not a date — use yyyy-MM-dd HH:mm";
        }

        if (existing is null) group.Tasks.Add(task);

        // settings group.linkedDelays: editing one task pushes its delays to the siblings
        var linked = Cybersole.Core.Store.TaskGroupSync.ApplyLinkedDelays(group, task);
        if (linked > 0)
            _services.Bus.Info("Task", $"linked delays applied to {linked} task(s) in '{group.Name}'");

        _services.Config.Save();
        _services.Bus.Info("Task", $"{(existing is null ? "created" : "updated")} {task.Name} → {uri.Host} ({task.Store})");
        Close();
    }
}
