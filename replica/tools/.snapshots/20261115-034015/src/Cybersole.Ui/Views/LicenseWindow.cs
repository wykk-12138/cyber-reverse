using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// License entry dialog — drives LicenseService.VerifyLicenseAsync, which had no UI entry point.
/// </summary>
public sealed class LicenseWindow : Window
{
    private readonly AppServices _services;
    private readonly TextBox _key = new() { Width = 320, Watermark = "license key" };
    private readonly TextBlock _status = new() { TextWrapping = TextWrapping.Wrap, Opacity = 0.85 };

    public LicenseWindow(AppServices services)
    {
        _services = services;
        Title = "License";
        Width = 460;
        Height = 220;
        CanResize = false;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        _key.Text = _services.Config.Settings.License ?? string.Empty;

        var verify = new Button { Content = "Verify", IsDefault = true, Padding = new Thickness(16, 5) };
        verify.Click += async (_, _) => await VerifyAsync();

        var cancel = new Button { Content = "Close" };
        cancel.Click += (_, _) => Close();

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Children = { cancel, verify },
        };

        Content = new StackPanel
        {
            Margin = new Thickness(18),
            Spacing = 10,
            Children =
            {
                new TextBlock { Text = "License key", Opacity = 0.8 },
                _key,
                _status,
                buttons,
            },
        };
    }

    private async Task VerifyAsync()
    {
        var key = _key.Text?.Trim();
        if (string.IsNullOrWhiteSpace(key))
        {
            _status.Text = "Enter a license key.";
            return;
        }

        _status.Text = "verifying…";
        try
        {
            // ConfigureAwait(true) on purpose: VerifyLicenseAsync awaits the network with
            // ConfigureAwait(false), so without this the continuation lands on a pool thread and
            // the _status.Text writes below throw "Call from invalid thread". Round 121.
            var ok = await _services.License.VerifyLicenseAsync(key).ConfigureAwait(true);
            _status.Text = ok
                ? $"accepted — saved to settings.json"
                : "rejected by the license API";
            if (ok) _services.Config.Save();
        }
        catch (Exception ex)
        {
            _status.Text = $"failed: {ex.Message}";
        }
    }
}
