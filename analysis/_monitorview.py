import io, os
src = '''using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Monitor;

/// <summary>
/// The monitor feed page (Cybersole.Ui.Views.Monitor.MonitorView).
///
/// <para>
/// R423: the replica had no such page — <c>Monitor.*</c> was the last locale family with no host class (7 values). What is
/// built here is **only what the image states in words**: the tab label, the search placeholder, the two empty states and the
/// sizes caption. The layout inside the feed (row shape, columns, badges) is NOT verified — no GUI session reached this
/// page, so it stays deliberately plain: a search box, a list, and the empty block.
/// </para>
/// </summary>
public sealed class MonitorView : UserControl
{
    /// <summary>"Monitor Feed" — the tab label (Monitor.Tab.Feed).</summary>
    public const string TabLabel = "Monitor Feed";

    /// <summary>"Search feed" — the search box's placeholder (Monitor.SearchPlaceholder).</summary>
    public const string SearchPlaceholder = "Search feed";

    /// <summary>"Waiting for monitor entries" — the idle headline (Monitor.Empty).</summary>
    public const string EmptyHeadline = "Waiting for monitor entries";

    /// <summary>"New products and restocks will appear here" (Monitor.Empty.Nothing.Subtitle).</summary>
    public const string EmptySubtitle = "New products and restocks will appear here";

    /// <summary>"No results" — the headline when a search matches nothing (Monitor.Empty.NoResults.Title).</summary>
    public const string NoResultsTitle = "No results";

    /// <summary>"Available sizes" (Monitor.Sizes.Available).</summary>
    public const string SizesAvailable = "Available sizes";

    /// <summary>"No available sizes" (Monitor.Sizes.None).</summary>
    public const string SizesNone = "No available sizes";

    private readonly ListBox _feed = new() { Height = 320 };
    private readonly TextBox _search = new() { Watermark = SearchPlaceholder };
    private readonly TextBlock _emptyTitle = new() { Text = EmptyHeadline, Opacity = 0.8 };
    private readonly TextBlock _emptySubtitle = new() { Text = EmptySubtitle, Opacity = 0.6 };

    /// <summary>What the feed currently shows, so a test can read it back.</summary>
    public IReadOnlyList<string> Entries => _feed.ItemsSource?.Cast<string>().ToList() ?? new List<string>();

    /// <summary>The sizes caption for a product with <paramref name="count"/> sizes (Monitor.Sizes.*).</summary>
    public static string SizesCaption(int count) => count > 0 ? SizesAvailable : SizesNone;

    public MonitorView()
    {
        Title = TabLabel;

        _search.TextChanged += (_, _) =>
        {
            var query = _search.Text ?? string.Empty;
            var entries = Entries.Where(e => e.Contains(query, StringComparison.OrdinalIgnoreCase)).ToList();

            _feed.ItemsSource = entries;
            _feed.IsVisible = entries.Count > 0;
            _emptyTitle.Text = query.Length > 0 && entries.Count == 0 ? NoResultsTitle : EmptyHeadline;
            _emptySubtitle.IsVisible = query.Length == 0;
        };

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                new TextBlock { Text = TabLabel, FontSize = 18, FontWeight = Avalonia.Media.FontWeight.SemiBold },
                _search,
                _feed,
                _emptyTitle,
                _emptySubtitle,
            },
        };
    }

    /// <summary>Fills the feed with the given lines (the shape of a row is not verified — see the class remarks).</summary>
    public void SetEntries(IEnumerable<string> entries)
    {
        var list = entries?.ToList() ?? new List<string>();
        _feed.ItemsSource = list;
        _feed.IsVisible = list.Count > 0;
        _emptyTitle.Text = EmptyHeadline;
        _emptySubtitle.IsVisible = list.Count == 0;
    }
}
'''
os.makedirs(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Monitor", exist_ok=True)
io.open(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Monitor\MonitorView.cs", 'w', encoding='utf-8', newline='').write(src)
print('MonitorView.cs written')
