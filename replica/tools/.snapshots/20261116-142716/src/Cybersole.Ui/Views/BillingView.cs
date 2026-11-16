using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Ui.Views.Common;
using Cybersole.Ui.Views.Profiles;

namespace Cybersole.Ui.Views;

/// <summary>
/// The Billing tab — which the running 5.18.32 build draws as the <b>profiles</b> page (R208, measured).
///
/// <code>
///  PROFILE GROUPS      [Custom ▾]        ┌ 📁 Group 1 ⚙   No Profiles Loaded   [CSV Editor]  🔍 Search profiles
///  🔍 Search groups                      │ ☐ Profile ⇅ Email ⇅ Card Holder ⇅ Card ⇅ Shipping ⇅
///  [Group 1        0]                    │                      [Add Profile][Clear Profiles]
///  [New Group +]                         └ Nothing to see here / Add some profiles to get started
/// </code>
///
/// <para>
/// This file used to be a different shape: a "Billing groups" list with a Name field and New/Clone/Delete buttons.
/// None of that is on the window. The measured page is a two-pane profiles browser, and its labels are exact:
/// <c>PROFILE GROUPS</c>, <c>Search groups</c>, <c>No Profiles Loaded</c>, <c>CSV Editor</c>,
/// <c>Search profiles</c>, <c>Add Profile</c>, <c>Clear Profiles</c>,
/// <c>Add some profiles to get started</c>, and the five columns
/// <c>Profile / Email / Card Holder / Card / Shipping</c>.
/// </para>
///
/// <para>
/// The group model is <c>Config.BillingGroups</c> — the same collection the Accounts and Profiles pages use, which is
/// why the rail, the editor and this page never disagree about which profiles exist.
/// </para>
/// </summary>
public sealed class BillingView : UserControl
{
    /// <summary>The five column headers, in the window's order.</summary>
    public static readonly string[] Columns = { "Profile", "Email", "Card Holder", "Card", "Shipping" };

    /// <summary>The empty state, from the one place that owns it.</summary>
    public const string EmptyHeadline = EmptyView.Headline;

    /// <inheritdoc cref="EmptyHeadline"/>
    public static string EmptyBody => EmptyView.Bodies["profiles"];

    /// <summary>The subtitle the window prints for a group with nothing in it.</summary>
    public const string NoProfilesLoaded = "No Profiles Loaded";

    private readonly AppServices _services;
    private readonly Common.GroupGrid _groups = new();
    private readonly StackPanel _rows = new() { Spacing = 2 };
    private readonly TextBlock _groupTitle = new() { FontSize = 18, FontWeight = FontWeight.SemiBold };
    private readonly TextBlock _subtitle = UiKit.Status();
    private readonly TextBlock _status = UiKit.Status();
    private readonly TextBox _groupSearch;
    private readonly TextBox _profileSearch;
    private BillingGroup? _selected;
    // R211: the rail is the shared GroupGrid, so there is no ItemsSource to reassign and no re-entrancy to gate —
    // the grid raises no selection event of its own, it calls the pick callback once per click.
    private List<BillingGroup> _visible = new();

    public BillingView(AppServices services)
    {
        _services = services;
        _groupSearch = UiKit.Text(watermark: "Search groups", width: double.NaN);
        _profileSearch = UiKit.Text(watermark: "Search profiles", width: 220);

        _groupSearch.TextChanged += (_, _) => Refresh();
        _profileSearch.TextChanged += (_, _) => Refresh();

        var grid = new Grid
        {
            // R222: 324 px, the measured rail width (see ProxyView.RailWidth).
            ColumnDefinitions = new ColumnDefinitions("324,*"),
            Children = { BuildRail(), BuildBody() },
        };
        Grid.SetColumn(grid.Children[1], 1);

        Content = grid;
        Refresh();
    }

    private Control BuildRail()
    {
        var header = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        var caption = new TextBlock
        {
            Text = "PROFILE GROUPS", FontSize = 11, Opacity = 0.6, VerticalAlignment = VerticalAlignment.Center,
        };
        var order = new ComboBox { ItemsSource = new[] { "Custom", "Name", "Count" }, SelectedIndex = 0, Width = 110 };
        Grid.SetColumn(order, 1);
        header.Children.Add(caption);
        header.Children.Add(order);

        var bottom = new Button { Content = "New Group  +", HorizontalAlignment = HorizontalAlignment.Stretch };
        bottom.Click += (_, _) =>
        {
            var group = new BillingGroup { Name = "Group " + (_services.Config.BillingGroups.Count + 1) };
            _services.Config.BillingGroups.Add(group);
            _services.Config.Save();
            Refresh();
            _selected = group;
            Refresh();
            _status.Text = "Group added.";
        };

        var dock = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(bottom, Dock.Bottom);
        dock.Children.Add(bottom);
        dock.Children.Add(_groups);

        return new StackPanel
        {
            Spacing = 8,
            Margin = new Thickness(0, 0, 12, 0),
            Children = { header, _groupSearch, dock },
        };
    }

    private Control BuildBody()
    {
        var titleRow = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        titleRow.Children.Add(new TextBlock { Text = "📁", FontSize = 18, VerticalAlignment = VerticalAlignment.Center });
        titleRow.Children.Add(_groupTitle);
        var gear = new Button { Content = "⚙", Padding = new Thickness(6, 0) };
        gear.Click += (_, _) => _status.Text = "Group settings: " + (_selected?.Name ?? "none");
        titleRow.Children.Add(gear);

        var csv = new Button { Content = "CSV Editor" };
        csv.Click += (_, _) =>
        {
            var editor = new ProfileCsvEditorView(_services);
            if (TopLevel.GetTopLevel(this) is Window owner)
                _ = new ViewHostModal("CSV Editor", editor, 820, 600).ShowDialog(owner);
        };

        var head = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto,Auto") };
        head.Children.Add(titleRow);
        var search = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 6 };
        search.Children.Add(csv);
        search.Children.Add(_profileSearch);
        Grid.SetColumn(search, 1);
        head.Children.Add(search);

        var columns = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 24, Margin = new Thickness(4, 10, 0, 4) };
        columns.Children.Add(new TextBlock { Text = "☐", Width = 18 });
        foreach (var column in Columns)
            columns.Children.Add(new TextBlock { Text = column + "  ⇅", Opacity = 0.55, FontSize = 12 });

        var add = new Button { Content = "Add Profile", Background = Brushes.MediumSeaGreen };
        add.Click += (_, _) => AddProfile();
        var clear = new Button { Content = "Clear Profiles", Background = Brushes.IndianRed };
        clear.Click += (_, _) =>
        {
            if (_selected is null) return;
            _selected.Profiles.Clear();
            _services.Config.Save();
            Refresh();
            _status.Text = "Profiles cleared.";
        };

        var actions = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, HorizontalAlignment = HorizontalAlignment.Right };
        actions.Children.Add(add);
        actions.Children.Add(clear);

        var headerGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        headerGrid.Children.Add(columns);
        Grid.SetColumn(actions, 1);
        headerGrid.Children.Add(actions);

        return new StackPanel
        {
            Spacing = 6,
            Children = { head, _subtitle, headerGrid, new Border { Height = 1, Background = Brushes.Gray, Opacity = 0.2 }, _rows, _status },
        };
    }

    private void AddProfile()
    {
        if (_selected is null) return;

        var creator = new ProfileCreatorView(_services);
        if (TopLevel.GetTopLevel(this) is Window owner)
            _ = new ViewHostModal("Add Profile", creator, 760, 560).ShowDialog(owner);
        else
        {
            _selected.Profiles.Add(new Profile { Name = "Profile " + (_selected.Profiles.Count + 1) });
            _services.Config.Save();
            Refresh();
        }
    }

    /// <summary>Rebuilds the rail and the profile rows from the model, honouring both search boxes.</summary>
    public void Refresh()
    {
        var groupFilter = _groupSearch.Text ?? string.Empty;
        var selectedId = _selected?.Id;

        _visible = _services.Config.BillingGroups
            .Where(g => string.IsNullOrWhiteSpace(groupFilter)
                        || g.Name.Contains(groupFilter, StringComparison.OrdinalIgnoreCase))
            .ToList();

        _selected = _visible.FirstOrDefault(g => g.Id == selectedId) ?? _visible.FirstOrDefault();

        // R211: the shared rail. A click comes back as a key, so the lookup stays here where the group type lives.
        _groups.SetRows(
            _visible.Select(g => (g.Id, g.Name, g.Profiles.Count.ToString())),
            _selected?.Id,
            key =>
            {
                _selected = _visible.FirstOrDefault(g => g.Id == key);
                Refresh();
            });

        _groupTitle.Text = _selected?.Name ?? "No group";

        var profileFilter = _profileSearch.Text ?? string.Empty;
        var profiles = (_selected?.Profiles ?? new List<Profile>())
            .Where(p => string.IsNullOrWhiteSpace(profileFilter)
                        || p.Name.Contains(profileFilter, StringComparison.OrdinalIgnoreCase)
                        || (p.Email ?? string.Empty).Contains(profileFilter, StringComparison.OrdinalIgnoreCase))
            .ToList();

        _subtitle.Text = profiles.Count == 0 ? NoProfilesLoaded : profiles.Count + " profiles";

        _rows.Children.Clear();

        if (profiles.Count == 0)
        {
            // R209: one shared EmptyView instead of a hand-built block per page.
            var emptyBlock = EmptyView.For("profiles", 72);
            emptyBlock.Margin = new Thickness(0, 40);
            _rows.Children.Add(emptyBlock);
            return;
        }

        foreach (var profile in profiles)
        {
            // R223: measured column proportions, not equal stars. Header label left edges read at two window widths:
            //   1568: Profile 412  Email 550  Card Holder 727  Card 906  → 138 / 177 / 179 / 138
            //   1375: Profile 465  Email 558  Card Holder 678  Card 796  →  93 / 120 / 118 /  96
            //   ratio: 1.00      1.28        1.29         1.00
            // Shipping is the last column and absorbs the remainder, so like the Tasks table's Status it cannot be
            // measured from an empty table and stays at 1.
            var row = new Grid { ColumnDefinitions = new ColumnDefinitions("18,1.0*,1.28*,1.29*,1.0*,1.0*"), Margin = new Thickness(4, 2) };
            var values = new[]
            {
                string.Empty, profile.Name, profile.Email ?? string.Empty,
                (profile.FirstName + " " + profile.LastName).Trim(),
                Last4(profile.CardNumber), profile.Country ?? string.Empty,
            };

            for (var i = 0; i < values.Length; i++)
            {
                var cell = new TextBlock { Text = i == 0 ? "☐" : values[i], FontSize = 12, VerticalAlignment = VerticalAlignment.Center };
                Grid.SetColumn(cell, i);
                row.Children.Add(cell);
            }

            _rows.Children.Add(row);
        }
    }

    private static string Last4(string? card) =>
        string.IsNullOrWhiteSpace(card) ? string.Empty
            : card.Length <= 4 ? card
            : "•••• " + card[^4..];
}
