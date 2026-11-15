using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Sign-in dialog (Cybersole.Ui.Views.Auth). Drives AuthService.SignInAsync, which previously had
/// no UI entry point at all — the session label was display-only.
/// </summary>
public sealed class SignInWindow : Window
{
    private readonly AppServices _services;
    private readonly TextBox _email = new() { Watermark = "you@example.com", Width = 280 };
    private readonly TextBox _password = new() { PasswordChar = '•', Width = 280 };
    private readonly TextBlock _status = new() { TextWrapping = TextWrapping.Wrap, Opacity = 0.85 };
    private readonly TextBox _authCode = new() { Watermark = "authorization code", Width = 280 };

    public SignInWindow(AppServices services)
    {
        _services = services;
        Title = "Sign in";
        Width = 420;
        Height = 260;
        CanResize = false;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        var signIn = new Button { Content = "Sign in", IsDefault = true, Padding = new Thickness(18, 5) };
        signIn.Click += async (_, _) => await SubmitAsync();

        var cancel = new Button { Content = "Cancel" };
        cancel.Click += (_, _) => Close();

        // the desktop client normally hands the browser an OAuth URL and receives a code back
        var openBrowser = new Button { Content = "Sign in with browser" };
        openBrowser.Click += (_, _) =>
        {
            var url = _services.Auth.BuildOAuthUrl();
            try
            {
                System.Diagnostics.Process.Start(
                    new System.Diagnostics.ProcessStartInfo(url) { UseShellExecute = true });
                _status.Text = "browser opened — paste the authorization code below";
            }
            catch (Exception ex)
            {
                // the success line used to sit after the try block, so a failure was overwritten
                // by "browser opened" one statement later. Round 122 (same shape as round 103).
                _status.Text = $"cannot open browser: {ex.Message}";
            }
        };

        var exchange = new Button { Content = "Exchange code" };
        exchange.Click += async (_, _) => await ExchangeAsync();

        var oauthRow = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children = { openBrowser, exchange },
        };

        var grid = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("90,*"),
            RowDefinitions = new RowDefinitions("Auto,Auto,Auto,Auto,Auto"),
        };

        void Row(int i, string label, Control input)
        {
            var l = new TextBlock { Text = label, VerticalAlignment = VerticalAlignment.Center };
            Grid.SetRow(l, i); Grid.SetColumn(l, 0);
            Grid.SetRow(input, i); Grid.SetColumn(input, 1);
            grid.Children.Add(l);
            grid.Children.Add(input);
        }

        Row(0, "Email", _email);
        Row(1, "Password", _password);
        Row(2, "Auth code", _authCode);

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Children = { cancel, signIn },
        };
        Grid.SetRow(buttons, 4);
        Grid.SetColumnSpan(buttons, 2);
        grid.Children.Add(buttons);

        Grid.SetRow(_status, 3);
        Grid.SetColumnSpan(_status, 2);
        grid.Children.Add(_status);

        Content = new StackPanel
        {
            Margin = new Thickness(18),
            Spacing = 10,
            Children = { grid, oauthRow },
        };
    }

    private async Task ExchangeAsync()
    {
        var code = _authCode.Text?.Trim();
        if (string.IsNullOrWhiteSpace(code))
        {
            _status.Text = "Paste the authorization code first.";
            return;
        }

        _status.Text = "exchanging code…";
        try
        {
            if (await _services.Auth.ExchangeCodeAsync(code).ConfigureAwait(true))
            {
                _services.Bus.Info("Auth", "signed in via browser OAuth");
                Close(true);
            }
            else
            {
                _status.Text = "Code exchange rejected.";
            }
        }
        catch (Exception ex)
        {
            _status.Text = $"failed: {ex.Message}";
        }
    }

    private async Task SubmitAsync()
    {
        var email = _email.Text?.Trim();
        var password = _password.Text ?? string.Empty;

        if (string.IsNullOrWhiteSpace(email))
        {
            _status.Text = "Email is required.";
            return;
        }

        _status.Text = "signing in…";
        try
        {
            var ok = await _services.Auth.SignInAsync(email, password).ConfigureAwait(true);
            if (ok)
            {
                _services.Bus.Info("Auth", $"signed in as {email}");
                Close(true);
            }
            else
            {
                _status.Text = "Sign-in rejected by the API.";
            }
        }
        catch (Exception ex)
        {
            _status.Text = $"failed: {ex.Message}";
        }
    }
}
