using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Smart Actions editor (Cybersole.Ui.Views.Settings — rules backed by smartActions.json).
/// Left: rule list, right: form for the selected rule.
/// </summary>
public sealed class SmartActionEditorWindow : Window
{
    private readonly AppServices _services;
    private readonly ListBox _list = new() { Width = 220, Background = Brushes.Transparent };
    private readonly TextBox _name = new();
    private readonly ComboBox _trigger = new();
    private readonly ComboBox _kind = new();
    private readonly TextBox _target = new() { Watermark = "webhook URL / notification text" };
    private readonly TextBox _storeFilter = new() { Watermark = "shopify (leave empty for all)" };
    private readonly TextBox _minPrice = new() { Watermark = "0" };
    private readonly CheckBox _enabled = new() { Content = "Enabled", IsChecked = true };
    private readonly TextBlock _status = new() { Opacity = 0.8, TextWrapping = TextWrapping.Wrap };
    private SmartAction? _selected;

    public SmartActionEditorWindow(AppServices services)
    {
        _services = services;
        Title = "Smart actions";
        Width = 820;
        Height = 520;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        _trigger.ItemsSource = Enum.GetNames<SmartTrigger>();
        _trigger.SelectedIndex = 0;
        _kind.ItemsSource = Enum.GetNames<SmartActionKind>();
        _kind.SelectedIndex = 1;

        _list.SelectionChanged += (_, _) =>
        {
            if (_list.SelectedItem is string id)
                Load(_services.Config.SmartActions.Actions.FirstOrDefault(a => a.Id == id));
        };

        var add = new Button { Content = "New" };
        add.Click += (_, _) =>
        {
            var rule = new SmartAction { Name = $"Rule {_services.Config.SmartActions.Actions.Count + 1}" };
            _services.Config.SmartActions.Actions.Add(rule);
            _services.Config.Save();
            Refresh();
            _list.SelectedItem = rule.Id;
        };

        var remove = new Button { Content = "Delete" };
        remove.Click += (_, _) =>
        {
            if (_selected is null) return;
            _services.Config.SmartActions.Actions.RemoveAll(a => a.Id == _selected.Id);
            _services.Config.Save();
            _selected = null;
            Refresh();
            _status.Text = "Rule deleted.";
        };

        var save = new Button { Content = "Save", Padding = new Thickness(14, 5) };
        save.Click += (_, _) => Save();

        var left = new DockPanel { Width = 240 };
        var leftBar = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 6,
            Children = { add, remove },
        };
        DockPanel.SetDock(leftBar, Dock.Top);
        left.Children.Add(leftBar);
        left.Children.Add(_list);

        var form = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("130,*"),
            RowDefinitions = new RowDefinitions(string.Join(",", Enumerable.Repeat("Auto", 8))),
            Margin = new Thickness(12, 0, 0, 0),
        };

        void Row(int i, string label, Control input)
        {
            var l = new TextBlock { Text = label, VerticalAlignment = VerticalAlignment.Center };
            Grid.SetRow(l, i); Grid.SetColumn(l, 0);
            Grid.SetRow(input, i); Grid.SetColumn(input, 1);
            form.Children.Add(l);
            form.Children.Add(input);
        }

        Row(0, "Name", _name);
        Row(1, "Trigger", _trigger);
        Row(2, "Action", _kind);
        Row(3, "Target", _target);
        Row(4, "Store filter", _storeFilter);
        Row(5, "Min price", _minPrice);
        Row(6, "State", _enabled);
        Grid.SetRow(save, 7);
        Grid.SetColumn(save, 1);
        form.Children.Add(save);

        var right = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(_status, Dock.Bottom);
        right.Children.Add(_status);
        right.Children.Add(new ScrollViewer { Content = form });

        var root = new DockPanel { Margin = new Thickness(14), LastChildFill = true };
        DockPanel.SetDock(left, Dock.Left);
        root.Children.Add(left);
        root.Children.Add(right);
        Content = root;

        Refresh();
        if (_services.Config.SmartActions.Actions.Count > 0)
            _list.SelectedItem = _services.Config.SmartActions.Actions[0].Id;
    }

    private void Refresh()
    {
        var ids = _services.Config.SmartActions.Actions.Select(a => a.Id).ToList();
        _list.ItemsSource = ids;
        _status.Text = $"{ids.Count} rule(s) — stored in smartActions.json";
    }

    private void Load(SmartAction? rule)
    {
        _selected = rule;
        if (rule is null) return;

        _name.Text = rule.Name;
        _trigger.SelectedIndex = (int)rule.Trigger;
        _kind.SelectedIndex = (int)rule.Kind;
        _target.Text = rule.Target;
        _storeFilter.Text = rule.StoreFilter ?? string.Empty;
        _minPrice.Text = rule.MinPrice?.ToString("0.##") ?? string.Empty;
        _enabled.IsChecked = rule.Enabled;
    }

    private void Save()
    {
        if (_selected is null)
        {
            _status.Text = "Select or create a rule first.";
            return;
        }

        _selected.Name = string.IsNullOrWhiteSpace(_name.Text) ? _selected.Name : _name.Text!.Trim();
        _selected.Trigger = (SmartTrigger)Math.Max(0, _trigger.SelectedIndex);
        _selected.Kind = (SmartActionKind)Math.Max(0, _kind.SelectedIndex);
        _selected.Target = _target.Text ?? string.Empty;
        _selected.StoreFilter = string.IsNullOrWhiteSpace(_storeFilter.Text) ? null : _storeFilter.Text!.Trim();
        _selected.MinPrice = decimal.TryParse(_minPrice.Text, out var price) ? price : null;
        _selected.Enabled = _enabled.IsChecked ?? true;

        _services.Config.Save();
        _services.Bus.Info("SmartAction", $"saved rule '{_selected.Name}' ({_selected.Trigger} → {_selected.Kind})");
        _status.Text = $"Saved '{_selected.Name}'.";
    }
}
