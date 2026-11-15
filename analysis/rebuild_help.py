import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding="utf-8").read()

start_marker = "/// <summary>Need help (Cybersole.Ui.Views.Settings.HelpView).</summary>"
end_marker = "}\n\n/// <summary>\n/// Data (Cybersole.Ui.Views.Settings.DataView)"

start = t.find(start_marker)
if start < 0:
    raise SystemExit("HelpView start anchor not found")
if t.count(start_marker) != 1:
    raise SystemExit("HelpView anchor not unique")

# Find the end of the HelpView class: the next top-level class doc comment after HelpView.
nxt = t.find("/// <summary>\n/// Data (Cybersole.Ui.Views.Settings.DataView)", start)
if nxt < 0:
    nxt = t.find("public sealed class DataView : UserControl", start)
    if nxt > 0:
        # back up over its doc comment
        cut = t.rfind("/// <summary>", start, nxt)
        if cut > start:
            nxt = cut
if nxt <= start:
    raise SystemExit("could not find the end of HelpView")

new_view = '''/// <summary>
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
/// The replica had the three buttons and a comment saying <i>"there is no error index to search"</i>
/// — while <see cref="Cybersole.Stores.Flows.ErrorCatalog.All"/> had been holding all thirteen
/// entries, word for word, since an earlier round. The catalogue existed and nothing rendered it:
/// the "built but never bound" orphan, on the one page whose whole job is to show it.
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

        void Open(string url)
        {
            try
            {
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                {
                    FileName = url,
                    UseShellExecute = true,
                });
                status.Text = "Opened " + url;
            }
            catch (Exception ex)
            {
                status.Text = $"Could not open the browser: {ex.Message}. The address is {url}";
            }
        }

        var openCenter = new Button
        {
            Content = OpenCenterLabel,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
            HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            Padding = new Thickness(12, 8),
        };
        openCenter.Click += (_, _) => Open(DocsUrl);

        var search = UiKit.Text(watermark: SearchLabel);
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

'''

t = t[:start] + new_view + t[nxt:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("HelpView replaced (%d chars -> %d)" % (len(new_view), len(t)))
