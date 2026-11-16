using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Cybersole.Core.Models;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;

namespace Cybersole.Ui.Views.Common;

/// <summary>
/// The group list the left rail of three pages draws (R210).
///
/// <para>
/// Measured on 5.18.32: Proxies, Accounts and Billing all print the same row — the group name on the left, a muted
/// count badge on the right, the selected row tinted, and <c>No groups matched your search</c> when a filter excludes
/// everything. Each of those three pages hand-built that row (ProxyView's <c>BuildLeftPane</c> had it inline, and the
/// other two had near-copies). The original's view list has it as a class, <c>GroupGrid</c>.
/// </para>
///
/// <para>
/// The control is deliberately dumb: it is handed the rows to show and a callback for a click. Filtering, ordering and
/// what a group <i>is</i> stay with the page, because each page's group type is different
/// (<c>ProxyGroup</c>, <c>AccountGroup</c>, <c>BillingGroup</c>).
/// </para>
/// </summary>
public sealed class GroupGrid : UserControl
{
    /// <summary>Printed when a search excludes every group.</summary>
    public const string NoMatch = "No groups matched your search";

    private readonly StackPanel _rows = new() { Spacing = 2 };

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>DeleteGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand DeleteGroup { get; }

    public GroupGrid()
    {
        DeleteGroup = new RelayCommand(() => DeleteGroupCore());
        Content = _rows;
    }

    /// <summary>The group keys currently shown (bound as <c>Items</c>), in the order they are drawn.</summary>
    public IReadOnlyList<string> Items { get; private set; } = Array.Empty<string>();

    /// <summary>Which store the list is scoped to, empty for all of them (bound as <c>Store</c>; read-only in the image).</summary>
    public string Store { get; private set; } = string.Empty;

    /// <summary>The rows currently built, as <c>(name, badge)</c>. Read back by tests.</summary>
    public IReadOnlyList<(string Name, string Badge)> Rows { get; private set; } = Array.Empty<(string, string)>();

    /// <summary>
    /// Fills the grid. <paramref name="selectedKey"/> picks the tinted row; <paramref name="onPick"/> receives the key
    /// of the row that was clicked.
    /// </summary>
    public void SetRows(IEnumerable<(string Key, string Name, string Badge)> rows, string? selectedKey,
        Action<string>? onPick, IBrush? accent = null)
    {
        _selectedKey = selectedKey;
        _rows.Children.Clear();
        var built = new List<(string, string)>();
        var keys = new List<string>();

        foreach (var (key, name, badge) in rows)
        {
            built.Add((name, badge));
            keys.Add(key);

            var line = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
            line.Children.Add(new TextBlock { Text = name, VerticalAlignment = VerticalAlignment.Center });

            var count = new TextBlock
            {
                Text = badge,
                Opacity = 0.6,
                VerticalAlignment = VerticalAlignment.Center,
                HorizontalAlignment = HorizontalAlignment.Right,
            };
            Grid.SetColumn(count, 1);
            line.Children.Add(count);

            var selected = string.Equals(key, selectedKey, StringComparison.Ordinal);
            var hit = new Button
            {
                Content = line,
                Background = selected ? accent ?? new SolidColorBrush(Color.FromArgb(40, 120, 160, 255)) : Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(8, 5),
                HorizontalAlignment = HorizontalAlignment.Stretch,
                HorizontalContentAlignment = HorizontalAlignment.Stretch,
            };
            var target = key;
            hit.Click += (_, _) => onPick?.Invoke(target);
            _rows.Children.Add(hit);
        }

        Rows = built;
        Items = keys;

        if (built.Count == 0)
            _rows.Children.Add(new TextBlock
            {
                Text = NoMatch,
                Opacity = 0.6,
                Margin = new Thickness(6, 8, 6, 0),
            });
    }

    /// <summary>Convenience overload for a page whose rows have no identity beyond their name.</summary>
    private string? _selectedKey;

    /// <summary>The row key the caller last marked as selected.</summary>
    public string? SelectedKey => _selectedKey;

    /// <summary>Raised when the bound command asks to delete the selected group (bound as <c>DeleteGroup</c>).</summary>
    public Action<string>? DeleteRequested { get; set; }

    /// <summary>
    /// Asks the owner to delete the selected group (bound as <c>DeleteGroup</c> on the accounts rail). The grid does not
    /// own the document, so it reports which key was selected and lets the caller remove it. Returns false when nothing
    /// is selected or no handler is bound.
    /// </summary>
    private bool DeleteGroupCore()
    {
        if (DeleteRequested is null) return false;
        var selected = _selectedKey;
        if (string.IsNullOrWhiteSpace(selected)) return false;

        DeleteRequested(selected!);
        return true;
    }

    public void SetRows(IEnumerable<(string Name, string Badge)> rows) =>
        SetRows(rows.Select(r => (r.Name, r.Name, r.Badge)), null, null);
}
