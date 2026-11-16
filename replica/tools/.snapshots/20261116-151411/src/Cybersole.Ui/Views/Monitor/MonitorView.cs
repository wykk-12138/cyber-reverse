using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Monitor;

/// <summary>
/// The monitor feed page (Cybersole.Ui.Views.Monitor.MonitorView).
///
/// <para>
/// R423: the replica had no such page — <c>Monitor.*</c> was the last locale family with no host class (7 values). What was
/// built there is **only what the image states in words**: the tab label, the search placeholder, the two empty states and the
/// sizes caption. The layout inside the feed (row shape, columns, badges) is NOT verified — no GUI session reached this
/// page, so it stays deliberately plain: a search box, a list, and the empty block.
/// </para>
/// <para>
/// R434: the five bound commands were added (see <c>docs/R434_DECISIONS.md</c>). The evidence that they are
/// <b>binding targets</b> — not guesses — is the compiled XAML descriptor trio (Getter / Setter / Property) per member:
/// <c>OpenFilter</c> 0x1432111cd / 0x143211210 / 0x14363b623 · <c>View</c> 0x143211210 / 0x14363b668 ·
/// <c>OpenUrl</c> 0x14321141a / 0x14363b94b · <c>Quicktask</c> 0x14321189b / 0x1432118dd / 0x14363ba4e ·
/// <c>LinkChange</c> 0x143211967 / 0x1432119aa / 0x14363bab8.
/// A list page with a selected row is what those descriptors imply, so "the command acts on the current selection"
/// is a <b>structural</b> reading. What each command <i>does</i> is a different question — see the three hooks below.
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

    private readonly StackPanel _detail = new() { IsVisible = false, Spacing = 2 };
    private readonly TextBlock _detailText = new() { Opacity = 0.85 };

    private readonly List<string> _entries = new();
    private readonly List<MonitorEvent> _events = new();
    private readonly MonitorFilters _filters;

    private MonitorEvent? _selectedEvent;

    public MonitorView() : this(null)
    {
    }

    /// <summary>
    /// <paramref name="settings"/> supplies the live <c>Settings.MonitorFilters</c> instance the original binds
    /// <c>OpenFilter</c> against (descriptor 0x1432111cd / 0x143211210, plus <c>Settings.MonitorFilters</c> in the
    /// same string). Passing null keeps a local fallback so the page still constructs in tests.
    /// </summary>
    public MonitorView(GlobalSettings? settings)
    {
        _filters = settings?.MonitorFilters ?? new MonitorFilters();

        View = new RelayCommand(ShowSelectedDetail);
        OpenFilter = new RelayCommand(() => FilterExposed = true);

        // The three hooks below are deliberately inert until a host supplies a delegate.
        // structure only — behaviour unknown (claim C-monitor-openurl / C-monitor-linkchange / C-monitor-quicktask).
        // docs/PARITY_CLAIMS.md carries the matching Unknown rows; MonitorViewBehaviourPins asserts both sides exist.
        OpenUrl = new RelayCommand(() => RunHook(OpenUrlHook, "C-monitor-openurl"));
        LinkChange = new RelayCommand(() => RunHook(LinkChangeHook, "C-monitor-linkchange"));
        Quicktask = new RelayCommand(() => RunHook(QuicktaskHook, "C-monitor-quicktask"));

        _search.TextChanged += (_, _) => ApplySearch();
        _feed.SelectionChanged += (_, _) =>
        {
            if (_feed.SelectedIndex >= 0 && _feed.SelectedIndex < _events.Count)
                SelectedEvent = _events[_feed.SelectedIndex];
        };

        _detail.Children.Add(_detailText);

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
                _detail,
            },
        };
    }

    // ---- bound commands (XAML binding targets, see the class remarks for the descriptor addresses) ----

    /// <summary>
    /// Shows the selected event's detail block (bound as <c>View</c>; descriptor 0x14363b668).
    /// <para>Observable behaviour: after invoking it, <see cref="DetailVisible"/> is true and
    /// <see cref="DetailText"/> equals <see cref="DetailLine"/> of the event selected at that moment.</para>
    /// </summary>
    public ICommand View { get; }

    /// <summary>
    /// Surfaces the <c>Settings.MonitorFilters</c> instance the original binds (bound as <c>OpenFilter</c>;
    /// descriptor 0x14363b623). After invoking it, <see cref="FilterExposed"/> is true and
    /// <see cref="Filters"/> is the same instance the constructor received.
    /// </summary>
    public ICommand OpenFilter { get; }

    /// <summary>
    /// structure only — behaviour unknown (claim C-monitor-openurl). The host may supply
    /// <see cref="OpenUrlHook"/>; when none is supplied invoking this command performs no side effect
    /// (no browser, no clipboard, no request) and only records <see cref="LastHookNote"/>.
    /// How the original opens a product URL — external browser or an embedded one — is not established;
    /// it needs main-window GUI observation or pseudocode-level comparison.
    /// </summary>
    public ICommand OpenUrl { get; }

    /// <summary>
    /// structure only — behaviour unknown (claim C-monitor-linkchange). Host hook via <see cref="LinkChangeHook"/>;
    /// inert when unset. The locale carries <c>Monitor.LinkChange</c> as copy only — whether it rewrites the selected
    /// link, the whole feed, or a batch selection is not established.
    /// </summary>
    public ICommand LinkChange { get; }

    /// <summary>
    /// structure only — behaviour unknown (claim C-monitor-quicktask). Host hook via <see cref="QuicktaskHook"/>;
    /// inert when unset. <c>Monitor.LaunchQuicktask</c> is copy only — whether it creates a task, seeds the task
    /// creator, or copies to the clipboard is not established.
    /// </summary>
    public ICommand Quicktask { get; }

    // ---- host hooks (default null: the commands must not pretend to work) ----

    /// <summary>Supplied by the host; receives the event selected at invocation time. Null = inert.</summary>
    public Action<MonitorEvent>? OpenUrlHook { get; set; }

    /// <summary>Supplied by the host; receives the event selected at invocation time. Null = inert.</summary>
    public Action<MonitorEvent>? LinkChangeHook { get; set; }

    /// <summary>Supplied by the host; receives the event selected at invocation time. Null = inert.</summary>
    public Action<MonitorEvent>? QuicktaskHook { get; set; }

    /// <summary>Every event handed to a hook, in order — so a test can assert "it got the selection at that moment".</summary>
    public IReadOnlyList<MonitorEvent> HookTargets => _hookTargets;

    private readonly List<MonitorEvent> _hookTargets = new();

    /// <summary>Why the last hook invocation had no effect (null when a hook actually ran).</summary>
    public string? LastHookNote { get; private set; }

    /// <summary>The claim id the last inert invocation belongs to (null when a hook ran).</summary>
    public string? LastHookClaim { get; private set; }

    // ---- observable state ----

    /// <summary>The row the feed currently has selected (the subject every command acts on).</summary>
    public MonitorEvent? SelectedEvent
    {
        get => _selectedEvent;
        set => _selectedEvent = value;
    }

    /// <summary>The monitor filters the page exposes (same instance as <c>Settings.MonitorFilters</c> when supplied).</summary>
    public MonitorFilters Filters => _filters;

    /// <summary>True once <see cref="OpenFilter"/> has been invoked.</summary>
    public bool FilterExposed { get; private set; }

    /// <summary>True once <see cref="View"/> has shown a detail block.</summary>
    public bool DetailVisible => _detail.IsVisible;

    /// <summary>The detail block's text (empty until <see cref="View"/> runs with a selection).</summary>
    public string DetailText => _detailText.Text ?? string.Empty;

    /// <summary>What the feed currently shows, so a test can read it back.</summary>
    public IReadOnlyList<string> Entries => _feed.ItemsSource?.Cast<string>().ToList() ?? new List<string>();

    /// <summary>What the sizes caption says for a product with <paramref name="count"/> sizes (Monitor.Sizes.*).</summary>
    public static string SizesCaption(int count) => count > 0 ? SizesAvailable : SizesNone;

    /// <summary>
    /// The detail line for one event. Built only from the fields the binding table proves exist
    /// (<c>MonitorEvent.Name/Store/Type/Timestamp</c>, descriptor 0x14321141a) — no new copy is invented here.
    /// </summary>
    public static string DetailLine(MonitorEvent e) =>
        string.Join(" · ", new[] { e.Name, e.Store, e.Type, e.Timestamp.ToString("u") }
            .Where(part => !string.IsNullOrEmpty(part)));

    /// <summary>The feed's row text for one event — same fields as <see cref="DetailLine"/>, no new copy.</summary>
    public static string EventLine(MonitorEvent e) =>
        string.IsNullOrEmpty(e.Store) ? e.Name : $"{e.Name} — {e.Store}";

    /// <summary>Fills the feed with the given lines (the shape of a row is not verified — see the class remarks).</summary>
    public void SetEntries(IEnumerable<string> entries)
    {
        _entries.Clear();
        _entries.AddRange(entries ?? Enumerable.Empty<string>());
        _feed.ItemsSource = _entries.ToList();
        _feed.IsVisible = _entries.Count > 0;
        _emptyTitle.Text = EmptyHeadline;
        _emptySubtitle.IsVisible = _entries.Count == 0;
    }

    /// <summary>Fills the feed with monitor events; <see cref="SelectedEvent"/> then follows the row selection.</summary>
    public void SetEvents(IEnumerable<MonitorEvent> events)
    {
        _events.Clear();
        _events.AddRange(events ?? Enumerable.Empty<MonitorEvent>());
        _feed.ItemsSource = _events.Select(EventLine).ToList();
        _feed.IsVisible = _events.Count > 0;
        _emptyTitle.Text = EmptyHeadline;
        _emptySubtitle.IsVisible = _events.Count == 0;
        _selectedEvent = _events.FirstOrDefault();
        if (_events.Count > 0) _feed.SelectedIndex = 0;
    }

    private void ApplySearch()
    {
        var query = _search.Text ?? string.Empty;
        var shown = _entries.Where(e => e.Contains(query, StringComparison.OrdinalIgnoreCase)).ToList();

        _feed.ItemsSource = shown;
        _feed.IsVisible = shown.Count > 0;
        _emptyTitle.Text = query.Length > 0 && shown.Count == 0 ? NoResultsTitle : EmptyHeadline;
        _emptySubtitle.IsVisible = query.Length == 0;
    }

    private void ShowSelectedDetail()
    {
        if (_selectedEvent is not { } e)
        {
            _detail.IsVisible = false;
            return;
        }

        _detailText.Text = DetailLine(e);
        _detail.IsVisible = true;
    }

    private void RunHook(Action<MonitorEvent>? hook, string claim)
    {
        if (_selectedEvent is not { } e)
        {
            LastHookNote = "no selection";
            LastHookClaim = claim;
            return;
        }

        _hookTargets.Add(e);

        if (hook is null)
        {
            LastHookNote = "no hook supplied — structure only, behaviour not implemented";
            LastHookClaim = claim;
            return;
        }

        LastHookNote = null;
        LastHookClaim = null;
        hook(e);
    }
}
