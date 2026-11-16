using System.Globalization;
using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Services;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Analytics;

/// <summary>
/// The Home page (Cybersole.Ui.Views.Analytics.AnalyticsView) — rebuilt in R205 against a snapshot of the real build.
///
/// <para>
/// The decompiled class gives the verbs: <c>ChangeChart</c>, <c>LoadAnalytics</c>, <c>MoveNext</c>,
/// <c>MovePrevious</c>, <c>OpenRelease</c>. It does not give the layout, and this replica had guessed one: a "Chart"
/// dropdown, Previous/Next buttons that page the TIME window, a ListBox for releases and no empty state.
/// </para>
///
/// <para>
/// The live window says otherwise, and this is what it says (measured, not remembered):
/// </para>
///
/// <code>
/// [ Checkouts | Spend ]            [ Today | Week | Month | Year ]        +----------------+
///      (0)                                                                 | Checkout Feed  |
///   Checkouts                                                              | Nothing to see |
///   ┌ nothing to see here ┐                                                | here / You     |
///   Nothing to see here                                                    | haven't made   |
///   You haven't made any checkouts for this period                         | any checkouts  |
///   Releases   &lt; 1 / 1 &gt;                                                   | yet            |
///   [ Palace Skateboards Winter '26 Week 7 / Nov 13 ]                      +----------------+
/// </code>
///
/// <para>
/// Two corrections follow from it. <b>The pager belongs to the releases, not to the period</b> — the arrows sit beside
/// "1 / 1" under Releases, and <c>MovePrevious</c>/<c>MoveNext</c> are what they call. And <b>the period is a
/// four-way selector</b> (Today/Week/Month/Year), not a Previous/Next window that walks one hour at a time.
/// </para>
/// </summary>
public sealed class AnalyticsView : UserControl
{
    /// <summary>The four chart kinds <c>ChangeChart</c> accepts, from the decompiled class.</summary>
    private static readonly string[] Charts =
        { "Checkouts", "Money spent", "Spend by store", "Timeline (last 12h)" };

    /// <summary>The four periods the window offers, in the order it offers them.</summary>
    public static readonly string[] Periods = { "Today", "Week", "Month", "Year" };

    /// <summary>The two segments above the number, measured from the window.</summary>
    public static readonly string[] Segments = { "Checkouts", "Spend" };

    /// <summary>
    /// The word under the big figure. The live window says "Money Spent" — capital S — on the Spend segment (R335);
    /// the replica used to say "Spend" and, before that, "Money spent".
    /// </summary>
    public static string SegmentCaption(int index) => index == 1 ? "Money Spent" : "Checkouts";

    /// <summary>
    /// The Spend figure as the window prints it: a dollar amount, <c>$0</c> when there is nothing (R335). The
    /// multi-digit format is inferred — the empty state is the only one the running build showed.
    /// </summary>
    public static string SpendFigure(decimal amount) => "$" + Math.Round(amount).ToString("0", CultureInfo.InvariantCulture);

    /// <summary>
    /// How the carousel pager reads. With nothing to page through the live window prints <c>0 / 0</c> (R334), not
    /// <c>1 / 1</c> — the page counter follows the number of pages, it does not default to one.
    /// </summary>
    public static string PagerCaption(int page, int pages) => pages <= 0 ? "0 / 0" : $"{page} / {pages}";

    /// <summary>The releases empty state's second line, verbatim from the running window (R334).</summary>
    public const string EmptyReleasesBody = "There are no upcoming releases";

    /// <summary>The two empty states, verbatim from the window.</summary>
    public const string EmptyHeadline = Common.EmptyView.Headline;

    /// <inheritdoc cref="EmptyHeadline"/>
    public static string EmptyPeriodBody => Common.EmptyView.Bodies["checkouts"];

    /// <inheritdoc cref="EmptyHeadline"/>
    public static string EmptyFeedBody => Common.EmptyView.Bodies["feed"];

    /// <summary>
    /// Opens one release (bound as <c>OpenRelease</c>). <c>ReleaseView</c> existed with Previous / Release / ShowGuide /
    /// ShowSitelist and nothing constructed it; this is the page that opens it, so the dialog title is the release's own
    /// product name. False when there is no window to host it.
    /// </summary>
    public bool OpenRelease(Release release)
    {
        if (release is null || TopLevel.GetTopLevel(this) is not Window) return false;

        Views.Common.ViewHostModal.Show(this, release.Product ?? "Release", new ReleaseView(_services, release));
        return true;
    }

    private readonly AppServices _services;
    private readonly StoreBarChart _chart = new() { Height = 170 };
    private readonly TextBlock _number = new() { FontSize = 26, FontWeight = FontWeight.Bold };
    private readonly TextBlock _caption = UiKit.Status();
    private readonly Control _emptyBlock;
    private readonly StackPanel _feed = new() { Spacing = 6 };
    private readonly StackPanel _releases = new()
    {
        Orientation = Orientation.Horizontal,
        Spacing = 12,
    };
    private readonly TextBlock _pageLabel = UiKit.Status();

    private DateTimeOffset _periodEnd = DateTimeOffset.UtcNow;
    private TimeSpan _periodWidth = TimeSpan.FromDays(1);
    private int _segment;
    private int _releasePage;

    // Building the segmented rows raises IsCheckedChanged for the default option. Without this flag the first
    // LoadAnalyticsCore() runs while the panels are still being attached, and the collection it mutates is the one being
    // built — measured as "Operations that change non-concurrent collections must have exclusive access".
    private bool _ready;

    // Avalonia keys radio groups by NAME inside one render root, so two AnalyticsView instances in the same app would
    // both register "seg-Checkouts" and the second one throws "An item with the same key has already been added".
    // Measured in R205 when two views were constructed in one test run. A per-instance suffix keeps the two rows of
    // THIS view exclusive without colliding with any other view.
    private static int _instances;
    private readonly string _groupTag = "seg-" + System.Threading.Interlocked.Increment(ref _instances);

    // ------------------------------------------------ bound commands (R254)
    //
    // The original binds ChangeChart / OpenRelease / MoveNext / MovePrevious on AnalyticsView
    // (analysis/xaml_bindings.json). The pager commands already exist; these two were missing.

    /// <summary>
    /// Switches the checkouts/spend segment (bound as <c>ChangeChart</c>). Returns false for an unknown segment name.
    /// </summary>
    public bool ChangeChart(string segment)
    {
        var index = Array.FindIndex(Segments, s => string.Equals(s, segment, StringComparison.OrdinalIgnoreCase));
        if (index < 0) return false;

        _segment = index;

        // changing the segment used to be a radio row; setting the field and reloading is the same effect
        _caption.Text = SegmentCaption(index);
        LoadAnalyticsCore();
        return true;
    }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>LoadAnalytics</c>; behaviour unchanged (was a method).</summary>
    public ICommand LoadAnalytics { get; }

    /// <summary>Bound as <c>MoveNext</c>; behaviour unchanged (was a method).</summary>
    public ICommand MoveNext { get; }

    /// <summary>Bound as <c>MovePrevious</c>; behaviour unchanged (was a method).</summary>
    public ICommand MovePrevious { get; }

    public AnalyticsView(AppServices services)
    {
        LoadAnalytics = new RelayCommand(LoadAnalyticsCore);
        MoveNext = new RelayCommand(MoveNextCore);
        MovePrevious = new RelayCommand(MovePreviousCore);

        _services = services;
        _caption.Text = "Checkouts";
        _emptyBlock = EmptyBlock();

        var left = new StackPanel
        {
            Spacing = 10,
            Children =
            {
                Segments2(Segments, i => { _segment = i; LoadAnalyticsCore(); }),
                Segments2(Periods, SetPeriodIndex),
                NumberRow(),
                _emptyBlock,
                ReleasesRow(),
                _releases,
            },
        };

        var right = new StackPanel
        {
            Spacing = 8,
            Children = { UiKit.Title("Checkout Feed"), _feed },
        };

        var grid = new Grid
        {
            // R221: measured at two window widths. Left panel / right panel = 973/521 at 1568 and 845/453 at 1375 —
            // 1.865 and 1.867, i.e. the same proportion, with a 24 px gutter. The replica had "2*,8,1*", which made
            // the checkout panel about 7% too wide and the feed panel too narrow.
            ColumnDefinitions = new ColumnDefinitions("1.87*,24,1*"),
            Children = { left, right },
        };
        Grid.SetColumn(right, 2);

        Content = new ScrollViewer { Content = grid };
        _ready = true;
        LoadAnalyticsCore();
    }

    private Control NumberRow()
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        row.Children.Add(_number);
        var label = UiKit.Status();
        label.Text = "Checkouts";
        row.Children.Add(label);
        return row;
    }

    /// <summary>A row of mutually exclusive labels, the way the window draws both of its segmented controls.</summary>
    private Control Segments2(IReadOnlyList<string> labels, Action<int> onPick)
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 4 };
        var group = _groupTag + "-" + labels[0];

        for (var i = 0; i < labels.Count; i++)
        {
            var index = i;
            var button = new RadioButton
            {
                Content = labels[i],
                GroupName = group,
                IsChecked = i == 0,
                Padding = new Thickness(14, 6),
            };
            button.IsCheckedChanged += (_, _) =>
            {
                if (_ready && button.IsChecked == true) onPick(index);
            };
            row.Children.Add(button);
        }

        return row;
    }

    private static Control EmptyBlock() =>
        // R209: the shared EmptyView owns the glyph, the headline and the second line.
        new Common.EmptyView(EmptyPeriodBody) { Margin = new Thickness(0, 24) };

    private Control ReleasesRow()
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        var title = UiKit.Status();
        title.Text = "Releases";
        title.FontSize = 14;
        title.FontWeight = FontWeight.SemiBold;

        var previous = new Button { Content = "‹", Padding = new Thickness(8, 2) };
        previous.Click += (_, _) => MovePreviousCore();
        var next = new Button { Content = "›", Padding = new Thickness(8, 2) };
        next.Click += (_, _) => MoveNextCore();

        row.Children.Add(title);
        row.Children.Add(previous);
        row.Children.Add(_pageLabel);
        row.Children.Add(next);
        return row;
    }

    /// <summary>Which period the window shows: [end - width, end).</summary>
    public (DateTimeOffset From, DateTimeOffset To) CurrentPeriod => (_periodEnd - _periodWidth, _periodEnd);

    /// <summary>The selected period name, for a caller that needs to say which view is on screen.</summary>
    public string SelectedPeriod { get; private set; } = Periods[0];

    /// <summary>Which page of the release carousel is showing (1-based, as the window prints it).</summary>
    public int ReleasePage => _releasePage + 1;

    /// <summary>
    /// How many pages the carousel has. Zero when there is nothing to page through: the live window prints
    /// <c>0 / 0</c> on a fresh install (R334), where an earlier reading with data showed <c>1 / 1</c>.
    /// </summary>
    public int ReleasePages => (_services.Stats.ByStoreInPeriod(CurrentPeriod.From, CurrentPeriod.To).Count + 2) / 3;

    /// <summary>Switches the period to one of <see cref="Periods"/> by name.</summary>
    public void SetPeriod(string period)
    {
        var index = Array.IndexOf(Periods, period);
        if (index < 0) return;
        SetPeriodIndex(index);
    }

    private void SetPeriodIndex(int index)
    {
        if (index < 0 || index >= Periods.Length) return;

        SelectedPeriod = Periods[index];
        _periodWidth = index switch
        {
            0 => TimeSpan.FromDays(1),
            1 => TimeSpan.FromDays(7),
            2 => TimeSpan.FromDays(30),
            _ => TimeSpan.FromDays(365),
        };
        _releasePage = 0;
        LoadAnalyticsCore();
    }

    /// <summary>Moves the release carousel back one page; the pager's left arrow.</summary>
    private void MovePreviousCore() => MoveTo(_releasePage - 1);

    /// <summary>Moves the release carousel forward one page; the pager's right arrow.</summary>
    private void MoveNextCore() => MoveTo(_releasePage + 1);

    private void MoveTo(int page)
    {
        // R746: a fresh install has no releases, and R334 measured the live window printing 0 / 0 there, so
        // ReleasePages == 0 is a documented normal state rather than an edge case. Math.Clamp(page, 0, -1) throws
        // on that state -- "'0' cannot be greater than -1" -- which would crash the pager the moment anyone
        // pressed an arrow before any release existed. There is no page to move to, so do nothing.
        if (ReleasePages <= 0)
        {
            return;
        }

        var clamped = Math.Clamp(page, 0, ReleasePages - 1);
        if (clamped == _releasePage) return;
        _releasePage = clamped;
        LoadAnalyticsCore();
    }

    /// <summary>Reloads the number, the chart, the release carousel and the feed for the current period.</summary>
    /// <remarks>
    /// R206: this rebuilds live <c>Children</c> collections. Called from a segmented control's handler while another
    /// thread is measuring the same view, Avalonia answers "Operations that change non-concurrent collections must have
    /// exclusive access" — measured one suite run in eight. The rebuild is posted to the UI thread when the caller is
    /// not on it, so the collections are only ever touched from the thread that owns them.
    /// </remarks>
    private void LoadAnalyticsCore()
    {
        if (!Avalonia.Threading.Dispatcher.UIThread.CheckAccess())
        {
            Avalonia.Threading.Dispatcher.UIThread.Post(() => LoadAnalytics.Execute(null));
            return;
        }

        var stats = _services.Stats;
        var (from, to) = CurrentPeriod;

        var (total, success, failed, spent) = stats.Summarize(from, to);
        var rate = total == 0 ? 0 : (double)success / total;

        // the number is what the window puts first: the count, with the segment's name under it
        _number.Text = _segment == 0 ? total.ToString() : SpendFigure(spent);
        _caption.Text = SegmentCaption(_segment);

        _emptyBlock.IsVisible = total == 0;

        var byStore = stats.ByStoreInPeriod(from, to).ToDictionary(kv => kv.Key, kv => kv.Value);
        if (_segment == 1)
        {
            // "Spend by store" is the chart ChangeChart reaches with the second segment here
            _chart.Update(byStore);
        }
        else
        {
            _chart.Update(byStore);
        }

        _pageLabel.Text = PagerCaption(ReleasePage, ReleasePages);

        _releases.Children.Clear();
        var cards = LoadReleases(byStore).ToList();
        if (cards.Count == 0)
        {
            // R334: the live empty state, verbatim.
            _releases.Children.Add(new TextBlock { Text = EmptyHeadline, FontWeight = FontWeight.SemiBold });
            _releases.Children.Add(new TextBlock { Text = EmptyReleasesBody, Opacity = 0.6, FontSize = 11 });
        }
        else
        {
            foreach (var card in cards.Skip(_releasePage * 3).Take(3))
                _releases.Children.Add(card);
        }

        _feed.Children.Clear();
        var events = stats.InPeriod(from, to);
        if (events.Count == 0)
        {
            _feed.Children.Add(new TextBlock { Text = EmptyHeadline, FontWeight = FontWeight.SemiBold });
            _feed.Children.Add(new TextBlock { Text = EmptyFeedBody, Opacity = 0.6, FontSize = 11 });
        }
        else
        {
            foreach (var e in events.OrderByDescending(e => e.At).Take(20))
            {
                _feed.Children.Add(new TextBlock
                {
                    Text = $"{e.At:HH:mm}  {e.Store ?? "?"}  {(e.Success ? "ok" : "fail")}  {e.Price:0.00}",
                    FontSize = 11,
                });
            }
        }

        _ = rate;
        _ = failed;
    }

    private static IEnumerable<Control> LoadReleases(IReadOnlyDictionary<string, (int Success, int Failed)> byStore)
    {
        // The feed comes from the release endpoint in the original; without a round-trip we surface what the checkout
        // history implies, as a card rather than a list row, because that is how the window draws it.
        foreach (var (store, counts) in byStore.OrderByDescending(kv => kv.Value.Success))
        {
            var card = new Border
            {
                Width = 200,
                Padding = new Thickness(10),
                Background = Brushes.Transparent,
                BorderBrush = Brushes.Gray,
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(6),
            };
            var body = new StackPanel { Spacing = 4 };
            body.Children.Add(new TextBlock { Text = store, FontWeight = FontWeight.SemiBold });
            body.Children.Add(new TextBlock
            {
                Text = $"{counts.Success} checkout(s), {counts.Failed} failed",
                FontSize = 11,
                Opacity = 0.7,
            });
            card.Child = body;
            yield return card;
        }
    }
}

/// <summary>
/// Checkout feed (Cybersole.Ui.Views.Analytics.CheckoutList) — Show opens the detail modal.
/// </summary>
public sealed class CheckoutList : UserControl
{
    /// <summary>Bound as <c>Show</c>; the button with that label runs this command.</summary>
    public ICommand Show { get; }


    private readonly ListBox _rows = new() { Height = 300 };
    private readonly TextBlock _status = UiKit.Status();
    private readonly AppServices _services;

    public CheckoutList(AppServices services)
    {
        _services = services;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Checkouts"),
                _rows,
                UiKit.Buttons(UiKit.Button("Show", () => Show.Execute(null))),
                _status,
            },
        };

        Refresh();
    
        Show = new RelayCommand(() => _status.Text =
                    _rows.SelectedItem is null
                        ? "Select a checkout."
                        : "Detail: " + _rows.SelectedItem);}

    public void Refresh() => _rows.ItemsSource = _services.Stats.Events
        .OrderByDescending(e => e.At)
        .Select(e => $"{e.At:yyyy-MM-dd HH:mm}  {e.Store ?? "?"}  {(e.Success ? "ok" : "fail")}  {e.Price}")
        .DefaultIfEmpty("(no checkouts)")
        .ToList();
}

/// <summary>
/// Checkout detail (Cybersole.Ui.Views.Analytics.Modals.CheckoutView) — Checkout / Close /
/// Next / OpenTracking / Previous / Properties, plus the CheckoutProperty key/value rows.
/// </summary>
public sealed class CheckoutView : UserControl
{

    // ------------------------------------------------ copy from the image's locale (R415)
    //
    // Checkout.OrderFormat / Checkout.OutForDelivery and Release.AddTasks / Release.Empty.CheckBack: the words the
    // analytics pages use, which had no counterpart anywhere in the source.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["OrderFormat"] = "Order {0}",   // Checkout.OrderFormat
        ["OutForDelivery"] = "Out for delivery",   // Checkout.OutForDelivery
        ["ScheduledDelivery"] = "Scheduled Delivery",   // Checkout.ScheduledDelivery
        ["ReleaseAddTasks"] = "Add Tasks",   // Release.AddTasks
        ["ReleaseEmptyCheckBack"] = "Check back later",   // Release.Empty.CheckBack
    };

    /// <summary>One of the image's analytics strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    private readonly List<CheckoutEvent> _events;
    private int _index;
    private readonly TextBlock _body = UiKit.Status();
    private readonly ListBox _properties = new() { Height = 160 };
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>
    /// R472: the original binds <c>Previous</c> / <c>Next</c> as **properties** on <c>CheckoutView</c>
    /// (binding table + the original's own descriptor table), and until now both buttons only wrote a
    /// sentence into the status line. Structure comes from the binding evidence; the *behaviour*
    /// (step one entry in the time-ordered list) is **inferred** — mark it as such, do not call it verified.
    /// </summary>
    public ICommand Previous { get; }

    /// <inheritdoc cref="Previous"/>
    public ICommand Next { get; }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>OpenTracking</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenTracking { get; }

    /// <summary>
    /// R710: bound as <c>Close</c>. The original's own compiled-XAML descriptors carry
    /// <c>Cybersole.Ui.Views.Analytics.Modals.CheckoutView,Cybersole.UI.Close!Getter</c>, so this name is a real
    /// binding member there rather than a button caption. Until now the button only wrote a sentence, which is the
    /// effect the original produces but not the structure it binds -- `analysis/c10_split.py` counted it as
    /// undeclared for exactly that reason.
    /// </summary>
    public ICommand Close { get; }

    public CheckoutView(AppServices services, IReadOnlyList<CheckoutEvent>? events = null, int index = 0)
    {
        OpenTracking = new RelayCommand(() => OpenTrackingCore());
        Close = new RelayCommand(() => Status("Closed."));

        _events = (events ?? services.Stats.Events).OrderByDescending(e => e.At).ToList();
        _index = Math.Clamp(index, 0, Math.Max(0, _events.Count - 1));
        Previous = new RelayCommand(() => Move(-1));
        Next = new RelayCommand(() => Move(1));

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Checkout"),
                _body,
                UiKit.Section("Properties", _properties),
                UiKit.Buttons(
                    UiKit.Button("Previous", () => Previous.Execute(null)),
                    UiKit.Button("Next", () => Next.Execute(null)),
                    UiKit.Button("Open tracking", () => OpenTrackingCore()),
                    UiKit.Button("Close", () => Close.Execute(null))),
                _status,
            },
        };

        Render();
    }

    /// <summary>Step through the entries; wraps at both ends so the buttons are never dead.</summary>
    private void Move(int delta)
    {
        if (_events.Count == 0) return;
        _index = (_index + delta + _events.Count) % _events.Count;
        Render();
    }

    /// <summary>
    /// Opens the store's tracking page for the checkout on screen (bound as <c>OpenTracking</c>).
    ///
    /// <para>
    /// R303: the button used to write "Opening tracking URL." to the status bar and do nothing. It now opens the URL the
    /// flow captured (<c>CheckoutOutcome.TrackingUrl</c> — Shopify sets it from <c>order_status_url</c>), and says so
    /// when the store did not return one.
    /// </para>
    /// </summary>
    private bool OpenTrackingCore()
    {
        if (_events.Count == 0) { Status("No checkout selected."); return false; }

        var current = _events[Math.Clamp(_index, 0, _events.Count - 1)];
        if (string.IsNullOrWhiteSpace(current.TrackingUrl))
        {
            Status("This checkout has no tracking URL.");
            return false;
        }

        if (TopLevel.GetTopLevel(this)?.Launcher is not { } launcher)
        {
            Status("This platform cannot open links.");
            return false;
        }

        launcher.LaunchUriAsync(new Uri(current.TrackingUrl!));
        Status("Opened " + current.TrackingUrl);
        return true;
    }

    private void Status(string text) => _status.Text = text;

    private void Render()
    {
        if (_events.Count == 0)
        {
            _body.Text = "No checkouts recorded yet.";
            _properties.ItemsSource = new List<string>();
            return;
        }

        var e = _events[_index];
        _body.Text =
            $"{e.Store ?? "?"}  ·  {(e.Success ? "success" : "failed")}  ·  {e.At:u}\n" +
            $"Product: {e.Product ?? "-"}\nPrice: {e.Price}\nProfile: {e.Profile ?? "-"}";

        _properties.ItemsSource = new List<string>
        {
            "store = " + (e.Store ?? "-"),
            "success = " + e.Success,
            "price = " + e.Price,
            "profile = " + (e.Profile ?? "-"),
            "at = " + e.At.ToString("u"),
        };
    }
}

/// <summary>
/// Release detail (Cybersole.Ui.Views.Analytics.Modals.ReleaseView) — Close / Next /
/// Previous / Release / ShowGuide / ShowSitelist.
/// </summary>
public sealed class ReleaseView : UserControl
{
    /// <summary>Bound as <c>Next</c>; the button with that label runs this command.</summary>
    public ICommand Next { get; }

    /// <summary>Bound as <c>Previous</c>; the button with that label runs this command.</summary>
    public ICommand Previous { get; }


    private readonly Release _release;
    private readonly TextBlock _status = UiKit.Status();

    private readonly AppServices _releaseServices;

    /// <summary>
    /// Shows the release's site list (bound as <c>ShowSitelist</c>). The locale names the tab — "Release.Tab.Sitelist" =
    /// "Sitelist" — and <c>ReleaseSitelistView</c> is that list, which nothing constructed until now.
    /// </summary>
    private bool ShowSitelistCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window) return false;

        Views.Common.ViewHostModal.Show(this, "Sitelist", new ReleaseSitelistView(_releaseServices, _release));
        return true;
    }

    /// <summary>
    /// Shows the buying guide for this release (bound as <c>ShowGuide</c>). R261: <c>ReleaseGuideView</c> existed and had
    /// never been constructed by anything.
    /// </summary>
    private bool ShowGuideCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window owner) return false;
        Views.Common.ViewHostModal.Show(this, "Buying guide", new ReleaseGuideView(_releaseServices, _release));
        return true;
    }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>ShowGuide</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowGuide { get; }

    /// <summary>Bound as <c>ShowSitelist</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowSitelist { get; }

    /// <summary>
    /// R710: bound as <c>Close</c>. The original's descriptor table carries
    /// <c>Cybersole.Ui.Views.Analytics.Modals.ReleaseView,Cybersole.UI.Close!Getter</c>, so this is a real binding
    /// member there rather than a caption on a button.
    /// </summary>
    public ICommand Close { get; }

    public ReleaseView(AppServices services, Release? release = null)
    {
        ShowGuide = new RelayCommand(() => ShowGuideCore());
        ShowSitelist = new RelayCommand(() => ShowSitelistCore());
        Close = new RelayCommand(() => Status("Closed."));

        _releaseServices = services;
        _release = release ?? new Release { Product = "(no release selected)" };

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Release"),
                UiKit.Section("Details",
                    UiKit.Row("Product", new TextBlock { Text = _release.Product ?? "-" }),
                    UiKit.Row("Price", new TextBlock { Text = _release.Price ?? "-" }),
                    UiKit.Row("Release date", new TextBlock
                    {
                        Text = _release.ReleaseDate?.ToString("u") ?? "-",
                    }),
                    UiKit.Row("Drops", new TextBlock { Text = _release.Drops.Count.ToString() })),
                UiKit.Buttons(
                    UiKit.Button("Previous", () => Previous.Execute(null)),
                    UiKit.Button("Next", () => Next.Execute(null)),
                    UiKit.Button("Show guide", () => Status("Buying guide opened.")),
                    UiKit.Button("Show site list", () => Status(
                        $"{_release.Drops.SelectMany(d => d.Stores).Distinct().Count()} store(s) in this release.")),
                    UiKit.Button("Close", () => Close.Execute(null))),
                _status,
            },
        };
    
        Next = new RelayCommand(() => Status("Next release."));
        Previous = new RelayCommand(() => Status("Previous release."));}

    private void Status(string text) => _status.Text = text;
}

/// <summary>
/// Release site list (Cybersole.Ui.Views.Analytics.Modals.ReleaseSitelistView) —
/// Release + Create task per store.
/// </summary>
public sealed class ReleaseSitelistView : UserControl
{
    private readonly ListBox _stores = new() { Height = 260 };
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>
    /// R473: the original binds <c>Create</c> as a **property** on this view. The action itself already
    /// worked (it appends a task to the first group and saves); only its exposure changes here.
    /// </summary>
    public ICommand Create { get; }

    public ReleaseSitelistView(AppServices services, Release? release = null)
    {
        var rel = release ?? new Release();
        var stores = rel.Drops
            .SelectMany(d => d.Stores.Select(s => (Store: s, Drop: d)))
            .DistinctBy(x => x.Store)
            .ToList();

        _stores.ItemsSource = stores.Count == 0
            ? new List<string> { "(no stores listed)" }
            : stores.Select(x => $"{x.Store}  —  {x.Drop.Time:u}  {x.Drop.Type}").ToList();

        Create = new RelayCommand(() =>
        {
            if (_stores.SelectedIndex < 0 || _stores.SelectedIndex >= stores.Count)
            {
                _status.Text = "Select a store first.";
                return;
            }

            var group = services.Config.TaskGroups.FirstOrDefault();
            if (group is null)
            {
                _status.Text = "Create a task group first.";
                return;
            }

            var store = stores[_stores.SelectedIndex].Store;
            group.Tasks.Add(new BotTask
            {
                Name = $"{rel.Product ?? "drop"} @ {store}",
                Store = store,
                Product = new Product { Name = rel.Product, Price = rel.Price },
            });
            services.Config.Save();
            _status.Text = $"Task created for {store}.";
        });

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Release sites"),
                _stores,
                UiKit.Buttons(UiKit.Button("Create", () => Create.Execute(null))),
                _status,
            },
        };
    }
}

/// <summary>Release guide (Cybersole.Ui.Views.Analytics.Modals.ReleaseGuideView).</summary>
public sealed class ReleaseGuideView : UserControl
{
    public ReleaseGuideView(AppServices services, Release? release = null)
    {
        var rel = release ?? new Release();

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Title("Buying guide"),
            UiKit.Caption($"How the {rel.Product ?? "release"} drop usually runs."),
            UiKit.Section("Before the drop",
                UiKit.Caption("1. Warm the proxies you intend to use."),
                UiKit.Caption("2. Open the store and solve the captcha once."),
                UiKit.Caption("3. Set monitor delays a few hundred ms above the store's rate limit.")),
            UiKit.Section("At the drop",
                UiKit.Caption("1. Start tasks a second or two early with stagger start."),
                UiKit.Caption("2. Watch the step list — a failure names the frame that broke."),
                UiKit.Caption("3. Keep one task in monitor-only mode as a canary.")),
            UiKit.Section("After",
                UiKit.Caption("Check Analytics for the success rate and the spend total."),
                UiKit.Caption($"Stores involved: {rel.Drops.SelectMany(d => d.Stores).Distinct().Count()}"))));
    }
}
