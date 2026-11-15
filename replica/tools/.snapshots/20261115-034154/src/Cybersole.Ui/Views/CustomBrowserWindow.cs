using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Browser shell (Cybersole.Ui.Views.Browser.CustomBrowser).
/// The original embeds DotNetBrowser/Chromium; this replica drives the same
/// navigation through <c>NetClient</c> and shows the fetched document + status,
/// which is enough for queue/captcha diagnostics without shipping a browser engine.
///
/// R16 adds the recovered command surface — Back / Forward / Refresh / Minimise / Exit —
/// plus the Autofill panel, which stages a profile's checkout values for pasting into a
/// page this shell cannot script.
/// </summary>
public sealed class CustomBrowserWindow : Window
{
    private readonly AppServices _services;
    private readonly TextBox _address = new()
    {
        Text = "https://example.com/",
        Width = 620,
        FontFamily = new FontFamily("Consolas,monospace"),
    };
    private readonly TextBlock _status = new() { Opacity = 0.8, Margin = new Thickness(0, 6) };
    private readonly TextBox _content = new()
    {
        IsReadOnly = true,
        AcceptsReturn = true,
        FontFamily = new FontFamily("Consolas,monospace"),
        TextWrapping = TextWrapping.NoWrap,
        Background = Brushes.Transparent,
    };

    private readonly List<string> _history = new();
    private int _historyIndex = -1;

    private readonly StackPanel _autofillRows = new() { Spacing = 2 };
    private readonly ComboBox _profilePicker = new() { Width = 220 };
    private readonly TextBlock _autofillStatus = new() { Opacity = 0.7 };

    private List<Profile> _profiles = new();

    public CustomBrowserWindow(AppServices services)
    {
        _services = services;
        Title = "Browser";
        Width = 1080;
        Height = 680;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        var back = new Button { Content = "←", Padding = new Thickness(10, 2) };
        back.Click += async (_, _) => await StepHistory(-1);

        var forward = new Button { Content = "→", Padding = new Thickness(10, 2) };
        forward.Click += async (_, _) => await StepHistory(+1);

        var go = new Button { Content = "Go", Padding = new Thickness(14, 4) };
        go.Click += async (_, _) => await Navigate(_address.Text);

        var reload = new Button { Content = "Refresh" };
        reload.Click += async (_, _) => await Navigate(_address.Text);

        var minimise = new Button { Content = "Minimise" };
        minimise.Click += (_, _) => WindowState = WindowState.Minimized;

        var exit = new Button { Content = "Exit" };
        exit.Click += (_, _) => Close();

        // transport picker: lets the user verify each TLS path against a live site
        var transport = new ComboBox
        {
            Width = 150,
            ItemsSource = Enum.GetNames<Cybersole.Http.TransportMode>(),
            SelectedIndex = (int)_services.Http.Transport,
        };
        transport.SelectionChanged += (_, _) =>
        {
            if (transport.SelectedIndex >= 0)
                _services.Http.Transport = (Cybersole.Http.TransportMode)transport.SelectedIndex;
        };

        var bar = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 6,
            Children = { back, forward, _address, go, reload, transport, minimise, exit },
        };

        var root = new DockPanel { Margin = new Thickness(12), LastChildFill = true };

        var top = new StackPanel { Spacing = 6, Children = { bar, _status } };
        DockPanel.SetDock(top, Dock.Top);
        root.Children.Add(top);

        var side = BuildAutofillPanel();
        DockPanel.SetDock(side, Dock.Right);
        root.Children.Add(side);

        root.Children.Add(_content);
        Content = root;

        LoadProfiles();
    }

    // ── autofill ─────────────────────────────────────────────────────────────

    private Control BuildAutofillPanel()
    {
        _profilePicker.SelectionChanged += (_, _) => RebuildAutofill();

        return new Border
        {
            Width = 280,
            Margin = new Thickness(10, 0, 0, 0),
            Padding = new Thickness(8),
            BorderThickness = new Thickness(1, 0, 0, 0),
            BorderBrush = Brushes.DimGray,
            Child = new DockPanel
            {
                LastChildFill = true,
                Children =
                {
                    BuildAutofillHeader(),
                    new ScrollViewer { Content = _autofillRows },
                },
            },
        };
    }

    private Control BuildAutofillHeader()
    {
        var panel = new StackPanel
        {
            Spacing = 4,
            Margin = new Thickness(0, 0, 0, 8),
            Children =
            {
                new TextBlock { Text = "Autofill", FontWeight = FontWeight.SemiBold },
                _profilePicker,
                new Button { Content = "Copy all as JSON", HorizontalAlignment = HorizontalAlignment.Left },
                _autofillStatus,
            },
        };

        var copyAll = (Button)panel.Children[2];
        copyAll.Click += async (_, _) => await CopyAllAsync();

        DockPanel.SetDock(panel, Dock.Top);
        return panel;
    }

    private void LoadProfiles()
    {
        _profiles = _services.Config.BillingGroups
            .SelectMany(g => g.Profiles)
            .ToList();

        _profilePicker.ItemsSource = _profiles.Count == 0
            ? new List<string> { "(no profiles)" }
            : _profiles.Select(p => $"{p.Name} — {p.Email}").ToList();

        if (_profiles.Count > 0) _profilePicker.SelectedIndex = 0;
        RebuildAutofill();
    }

    /// <summary>The field/value pairs the original autofill would type into the page.</summary>
    private IReadOnlyList<(string Field, string Value)> AutofillFields(Profile profile)
    {
        var fields = new List<(string, string)>
        {
            ("email", profile.Email ?? string.Empty),
            ("firstName", profile.FirstName ?? string.Empty),
            ("lastName", profile.LastName ?? string.Empty),
            ("phone", profile.Phone ?? string.Empty),
            ("address1", profile.Address1 ?? string.Empty),
            ("address2", profile.Address2 ?? string.Empty),
            ("city", profile.City ?? string.Empty),
            ("state", profile.State ?? string.Empty),
            ("zip", profile.Zip ?? string.Empty),
            ("country", profile.Country ?? string.Empty),
        };

        if (!string.IsNullOrEmpty(profile.CardNumber))
        {
            var expiry = profile.CardExpiry ?? string.Empty;
            var parts = expiry.Split('/', StringSplitOptions.RemoveEmptyEntries);

            fields.Add(("card.number", profile.CardNumber!));
            fields.Add(("card.expiry", expiry));
            fields.Add(("card.month", parts.Length > 0 ? parts[0].Trim() : string.Empty));
            fields.Add(("card.year", parts.Length > 1 ? parts[1].Trim() : string.Empty));
            fields.Add(("card.cvv", profile.CardCvv ?? string.Empty));
        }

        return fields;
    }

    private void RebuildAutofill()
    {
        _autofillRows.Children.Clear();

        var index = _profilePicker.SelectedIndex;
        if (index < 0 || index >= _profiles.Count)
        {
            _autofillStatus.Text = "No profile selected.";
            return;
        }

        var profile = _profiles[index];
        foreach (var (field, value) in AutofillFields(profile))
        {
            var row = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                Spacing = 6,
                Children =
                {
                    new TextBlock
                    {
                        Text = field,
                        Width = 88,
                        Opacity = 0.65,
                        FontSize = 11,
                        VerticalAlignment = VerticalAlignment.Center,
                    },
                    new TextBox
                    {
                        Text = field.StartsWith("card.", StringComparison.Ordinal) && field != "card.number"
                            ? new string('•', Math.Min(4, value.Length))
                            : value,
                        IsReadOnly = true,
                        FontSize = 11,
                        Width = 150,
                    },
                },
            };

            _autofillRows.Children.Add(row);
        }

        _autofillStatus.Text = $"{AutofillFields(profile).Count} fields staged.";
    }

    private async Task CopyAllAsync()
    {
        var index = _profilePicker.SelectedIndex;
        if (index < 0 || index >= _profiles.Count)
        {
            // used to return here without a word, so the button looked broken on a fresh profile
            _autofillStatus.Text = _profiles.Count == 0
                ? "No profiles yet — add one on the Billing page."
                : "Select a profile first.";
            return;
        }

        var payload = System.Text.Json.JsonSerializer.Serialize(
            AutofillFields(_profiles[index]).ToDictionary(kv => kv.Field, kv => kv.Value),
            new System.Text.Json.JsonSerializerOptions { WriteIndented = true });

        if (Clipboard is not null)
        {
            await Clipboard.SetTextAsync(payload).ConfigureAwait(true);
            _autofillStatus.Text = "Copied to clipboard.";
        }
        else
        {
            _autofillStatus.Text = "Clipboard unavailable.";
        }
    }

    // ── navigation ───────────────────────────────────────────────────────────

    private void SetAddress(string url) => _address.Text = url;

    private async Task StepHistory(int delta)
    {
        var next = _historyIndex + delta;
        if (next < 0 || next >= _history.Count) return;

        _historyIndex = next;
        await Navigate(_history[_historyIndex], record: false);
    }

    private async Task Navigate(string? rawUrl, bool record = true)
    {
        var url = rawUrl?.Trim();
        if (string.IsNullOrWhiteSpace(url)) return;

        _status.Text = "loading…";
        _content.Text = string.Empty;

        try
        {
            var res = await _services.Http.GetAsync(url!, new Cybersole.Http.RequestOptions
            {
                Timeout = TimeSpan.FromSeconds(20),
                Tag = "browser",
            }).ConfigureAwait(true);

            var via = res.Headers.GetValueOrDefault("X-Cyb-Transport");
            var alpn = res.Headers.GetValueOrDefault("X-Cyb-Alpn");
            _status.Text = $"HTTP {res.StatusCode}  {res.Bytes} bytes  {res.Protocol}  {res.Elapsed.TotalMilliseconds:0} ms" +
                           $"  server={(res.Headers.GetValueOrDefault("Server") ?? "-")}" +
                           (via is null ? string.Empty : $"  transport={via}") +
                           (alpn is null ? string.Empty : $"  alpn={alpn}");
            _content.Text = res.Body.Length > 200_000 ? res.Body[..200_000] + "\n…(truncated)" : res.Body;

            if (record)
            {
                // drop any forward entries, then append
                if (_historyIndex >= 0 && _historyIndex < _history.Count - 1)
                    _history.RemoveRange(_historyIndex + 1, _history.Count - _historyIndex - 1);

                if (_history.Count == 0 || _history[^1] != url)
                    _history.Add(url!);

                _historyIndex = _history.Count - 1;
            }

            _address.Text = url;
        }
        catch (Exception ex)
        {
            _status.Text = $"failed: {ex.Message}";
        }
    }

    /// <summary>Test hook: the URLs this window has visited.</summary>
    public IReadOnlyList<string> History => _history;
}
