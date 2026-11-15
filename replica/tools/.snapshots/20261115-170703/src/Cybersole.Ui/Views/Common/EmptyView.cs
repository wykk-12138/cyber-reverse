using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;

namespace Cybersole.Ui.Views.Common;

/// <summary>
/// The empty state every page in the running build shares (R209).
///
/// <para>
/// Measured on 5.18.32: Home, Tasks, Accounts, Proxies and Billing all draw the same thing where a list would be —
/// a circular glyph with an X, the headline <c>Nothing to see here</c>, and one page-specific line under it
/// (<c>You haven't made any checkouts for this period</c>, <c>Add some tasks to get started</c>,
/// <c>Add a group to get started</c>, <c>Add some proxies to get started</c>,
/// <c>Add some profiles to get started</c>).
/// </para>
///
/// <para>
/// This replica had that block hand-built in every page — six copies of the same three elements and the same headline
/// string. The original's own view list carries <c>EmptyView</c> as a class, which is why this file exists: one
/// control, one headline constant, and the page only supplies the second line.
/// </para>
/// </summary>
public sealed class EmptyView : UserControl
{
    /// <summary>The headline, verbatim. Every page uses this one string.</summary>
    public const string Headline = "Nothing to see here";

    /// <summary>The per-page second lines, as measured.</summary>
    public static readonly IReadOnlyDictionary<string, string> Bodies =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["checkouts"] = "You haven't made any checkouts for this period",
            ["feed"] = "You haven't made any checkouts yet",
            ["tasks"] = "Add some tasks to get started",
            ["accounts"] = "Add a group to get started",
            ["proxies"] = "Add some proxies to get started",
            ["profiles"] = "Add some profiles to get started",
            ["cloudflare"] = "Add a Cloudflare provider to get started",
            ["smartActions"] = "Add a smart action to get started",
        };

    /// <summary>
    /// The page-specific second line for <paramref name="key"/>, or the headline's default when the page has none.
    /// </summary>
    /// <remarks>
    /// R400: <c>Settings.CloudflareSolvers.EmptySubtitle</c> is "Add a Cloudflare provider to get started", while the page used
    /// to print the proxies sentence. Adding a key here is how a page gets its own line — the shared headline stays shared.
    /// </remarks>
    public static string Body(string key) => Bodies.TryGetValue(key, out var body) ? body : string.Empty;



    /// <summary>The headline element, so a test can read what is on screen without guessing the tree shape.</summary>
    public TextBlock HeadlineText { get; }

    /// <summary>The page-specific second line.</summary>
    public TextBlock BodyText { get; }

    /// <summary>The circular glyph the window draws above the headline.</summary>
    public Border Icon { get; }

    public EmptyView(string body, double iconSize = 96)
        : this(Headline, body, iconSize)
    {
    }

    /// <summary>
    /// The block with an overridden headline. Only <see cref="AccountTable"/> uses this today — the settings tables
    /// print their own title, and it is always <see cref="Headline"/> at the call sites.
    /// </summary>
    public EmptyView(string headline, string body, double iconSize = 96)
    {
        var panel = new StackPanel
        {
            Spacing = 6,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };

        var icon = new Border
        {
            Width = iconSize,
            Height = iconSize,
            CornerRadius = new CornerRadius(iconSize / 2),
            BorderThickness = new Thickness(2),
            BorderBrush = new SolidColorBrush(Color.FromArgb(60, 200, 200, 210)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Child = new TextBlock
            {
                Text = "✕",
                FontSize = iconSize * 0.3,
                Opacity = 0.45,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };
        Icon = icon;
        panel.Children.Add(icon);

        var headlineBlock = new TextBlock
        {
            Text = headline,
            FontWeight = FontWeight.SemiBold,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 10, 0, 0),
        };
        HeadlineText = headlineBlock;
        panel.Children.Add(headlineBlock);

        var bodyText = new TextBlock
        {
            Text = body,
            Opacity = 0.6,
            FontSize = 12,
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        BodyText = bodyText;
        panel.Children.Add(bodyText);

        Content = panel;
    }

    /// <summary>Builds the block by page key, so a page cannot invent its own second line.</summary>
    public static EmptyView For(string page, double iconSize = 96) =>
        new(Bodies.TryGetValue(page, out var body) ? body : string.Empty, iconSize);
}
