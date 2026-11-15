using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Captcha;

/// <summary>
/// Google sign-in dialog (Cybersole.Ui.Views.Captcha.GoogleLogin) — Close / Save.
/// The solver uses these accounts to keep reCAPTCHA scores healthy.
/// </summary>
public sealed class GoogleLogin : Window
{
    private readonly AppServices _services;
    private readonly TextBlock _status = UiKit.Status();

    public GoogleLogin(AppServices services, GoogleAccount? existing = null)
    {
        _services = services;

        Title = existing is null ? "Add Google account" : $"Edit {existing.Email}";
        Width = 480;
        Height = 340;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var email = UiKit.Text(existing?.Email, watermark: "name@gmail.com", width: 320);
        var name = UiKit.Text(existing?.Name, watermark: "Display name", width: 320);
        var proxy = UiKit.Text(existing?.Proxy, watermark: "host:port:user:pass", width: 320);
        var password = UiKit.Text(password: true, width: 320);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title(existing is null ? "Add Google account" : "Edit Google account"),
                UiKit.Form(
                    UiKit.Row("Email", email, 120),
                    UiKit.Row("Name", name, 120),
                    UiKit.Row("Password", password, 120),
                    UiKit.Row("Proxy", proxy, 120)),
                UiKit.Buttons(
                    new Button
                    {
                        Content = "Save",
                        Command = new RelayCommand(() =>
                        {
                            try
                            {
                                if (string.IsNullOrWhiteSpace(email.Text))
                                {
                                    _status.Text = "An email is required.";
                                    return;
                                }

                                var doc = services.Config.Accounts;
                                if (existing is null)
                                {
                                    doc.Google.Add(new GoogleAccount
                                    {
                                        Email = email.Text!,
                                        Name = name.Text,
                                        Proxy = proxy.Text,
                                        State = "Idle",
                                    });
                                }
                                else
                                {
                                    existing.Email = email.Text!;
                                    existing.Name = name.Text;
                                    existing.Proxy = proxy.Text;
                                }

                                services.Config.Save();
                                Close();
                            }
                            catch (Exception ex)
                            {
                                _status.Text = ex.Message;
                            }
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
                _status,
            },
        };
    }
}

/// <summary>
/// YouTube warm-up window (Cybersole.Ui.Views.Captcha.YoutubeWindow) — Account.
/// Plays watch time against a Google account so the session looks organic.
/// </summary>
public sealed class YoutubeWindow : Window
{
    private readonly AppServices _services;
    private readonly ListBox _accounts = new() { Height = 200 };
    private readonly TextBlock _status = UiKit.Status();

    public YoutubeWindow(AppServices services)
    {
        _services = services;

        Title = "YouTube warm-up";
        Width = 560;
        Height = 460;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title("YouTube"),
                UiKit.Caption("Watch time keeps an account's captcha score healthy."),
                UiKit.Row("Account", _accounts),
                UiKit.Buttons(
                    new Button
                    {
                        Content = "Open video",
                        Command = new RelayCommand(() =>
                        {
                            var account = SelectedAccount();
                            _status.Text = account is null
                                ? "Select an account."
                                : $"Warming {account.Email} on the configured proxy.";
                        }),
                    },
                    new Button
                    {
                        Content = "Add account",
                        Command = new RelayCommand(() =>
                        {
                            var login = new GoogleLogin(services);
                            _ = login.ShowDialog(this);
                            login.Closed += (_, _) => Refresh();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
                _status,
            },
        };

        Refresh();
    }

    public GoogleAccount? SelectedAccount()
    {
        var index = _accounts.SelectedIndex;
        var google = _services.Config.Accounts.Google;
        return index < 0 || index >= google.Count ? null : google[index];
    }

    public void Refresh() => _accounts.ItemsSource = _services.Config.Accounts.Google
        .Select(g => $"{g.Email}  ·  {g.State}  ·  {g.Proxy ?? "no proxy"}")
        .DefaultIfEmpty("(no Google accounts)")
        .ToList();
}
