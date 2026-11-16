using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Modals;

/// <summary>Message box flavour (Cybersole.Ui.Views.Modals.MessageBoxDialog.Type).</summary>
public enum MessageBoxType
{
    Info = 0,
    Warning = 1,
    Error = 2,
    Question = 3,
}

/// <summary>
/// Message box (Cybersole.Ui.Views.Modals.MessageBoxDialog) — ActionText / CancelText /
/// Confirm / Cancel / ShowAction / ShowCancel / TextAlignment / Title / Type.
/// </summary>
public sealed class MessageBoxDialog : Window
{
    // R253: the original binds these four on the dialog (analysis/xaml_bindings.json) instead of taking them as
    // constructor parameters. They are exposed here as members and the constructor keeps its parameters for the existing
    // call sites, so both shapes work and there is still one place that decides what the buttons say.

    /// <summary>
    /// What kind of message this is (bound as <c>Type</c>, R357). Same values the constructor already took: the dialog has
    /// carried a <see cref="MessageBoxType"/> since R253, it just was not exposed under the bound name.
    /// </summary>
    public MessageBoxType Type { get; set; } = MessageBoxType.Info;

    /// <summary>Label of the confirm button (bound as <c>ActionText</c>).</summary>
    public string ActionText { get; set; } = "OK";

    /// <summary>Label of the cancel button (bound as <c>CancelText</c>).</summary>
    public string CancelText { get; set; } = "Cancel";

    /// <summary>Whether the confirm button is shown (bound as <c>ShowAction</c>).</summary>
    public bool ShowAction { get; set; } = true;

    /// <summary>Whether the cancel button is shown (bound as <c>ShowCancel</c>).</summary>
    public bool ShowCancel { get; set; }

    /// <summary>Bound as <c>Cancel</c>: dismisses the dialog without confirming (the cancel button's command).</summary>
    public ICommand Cancel { get; }

    /// <summary>Bound as <c>Confirm</c>: the action button's command — sets <see cref="Confirmed"/> then closes.</summary>
    public ICommand Confirm { get; }

    /// <summary>
    /// Bound as <c>TextAlignment</c>. The message block used to hard-code <c>Left</c>; it now reads this property,
    /// so assigning it before showing the dialog takes effect.
    /// </summary>
    /// <remarks>
    /// The type is spelled out because a member named <c>TextAlignment</c> shadows <c>Avalonia.Media.TextAlignment</c>
    /// inside this class — `TextAlignment.Left` would resolve to the property, not the enum.
    /// </remarks>
    public Avalonia.Media.TextAlignment TextAlignment { get; set; } = Avalonia.Media.TextAlignment.Left;

    private void ConfirmCore()
    {
        Confirmed = true;
        Close();
    }

    public MessageBoxDialog(string title, string message,
        MessageBoxType type = MessageBoxType.Info,
        string actionText = "OK", string cancelText = "Cancel",
        bool showAction = true, bool showCancel = false)
    {
        Type = type;
        Title = title;
        Cancel = new RelayCommand(Close);
        Confirm = new RelayCommand(ConfirmCore);
        Width = 460;
        Height = 240;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var text = new TextBlock
        {
            Text = message,
            TextWrapping = TextWrapping.Wrap,
            TextAlignment = TextAlignment,
            Margin = new Thickness(0, 0, 0, 12),
        };

        var body = new StackPanel { Spacing = 8 };
        body.Children.Add(UiKit.Title(title));
        body.Children.Add(text);

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Margin = new Thickness(0, 12, 0, 0),
        };

        Confirmed = false;

        if (showAction)
        {
            buttons.Children.Add(new Button
            {
                Content = actionText,
                IsDefault = type != MessageBoxType.Question,
                Command = Confirm,
            });
        }

        if (showCancel)
        {
            buttons.Children.Add(new Button
            {
                Content = cancelText,
                Command = Cancel,
            });
        }

        if (!showAction && !showCancel) buttons.Children.Add(new Button { Content = "Close", Command = new RelayCommand(Close) });

        body.Children.Add(buttons);

        Content = new StackPanel { Margin = new Thickness(16) };
        ((StackPanel)Content).Children.Add(body);
    }

    /// <summary>True when the action button was pressed (MessageBoxDialog.Confirm).</summary>
    public bool Confirmed { get; private set; }

    public static MessageBoxDialog Info(string title, string message) =>
        new(title, message, MessageBoxType.Info);

    public static MessageBoxDialog Error(string title, string message) =>
        new(title, message, MessageBoxType.Error);

    // R519: was Confirm, which collided with the bound Confirm command (CS0102). It has no call sites, so it
    // is the one that moves. The bound name is the one the original uses; the convenience factory is ours.
    public static MessageBoxDialog Ask(string title, string message) =>
        new(title, message, MessageBoxType.Question, actionText: "Yes",
            cancelText: "No", showAction: true, showCancel: true);
}

/// <summary>
/// Single-line input (Cybersole.Ui.Views.Modals.InputModal) — Title / Placeholder /
/// ButtonText / Close.
/// </summary>
public sealed class InputModal : Window
{

    /// <summary>Label of the confirm button (bound as <c>ButtonText</c>).</summary>
    public string ButtonText { get; set; } = "OK";

    /// <summary>Watermark shown before anything is typed (bound as <c>Placeholder</c>).</summary>
    public string Placeholder { get; set; } = string.Empty;
    private readonly TextBox _input;

    public InputModal(string title, string placeholder = "", string buttonText = "OK")
    {
        Title = title;
        Width = 420;
        Height = 190;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        _input = UiKit.Text(watermark: placeholder, width: 360);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title(title),
                _input,
                UiKit.Buttons(
                    new Button
                    {
                        Content = buttonText,
                        Command = new RelayCommand(() =>
                        {
                            Accepted = true;
                            Close();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };
    }

    public bool Accepted { get; private set; }

    public string Value => _input.Text ?? string.Empty;
}

/// <summary>
/// Dropdown picker (Cybersole.Ui.Views.Modals.DropdownModal) — Title / Placeholder /
/// ButtonText.
/// </summary>
public sealed class DropdownModal : Window
{

    /// <summary>Label of the confirm button (bound as <c>ButtonText</c>).</summary>
    public string ButtonText { get; set; } = "OK";

    /// <summary>Watermark shown before anything is typed (bound as <c>Placeholder</c>).</summary>
    public string Placeholder { get; set; } = string.Empty;
    private readonly ComboBox _picker;

    public DropdownModal(string title, IEnumerable<string> options, string placeholder = "",
        string buttonText = "OK")
    {
        Title = title;
        Width = 420;
        Height = 200;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var list = options.ToList();
        _picker = UiKit.Combo(list, 0, width: 360);
        if (placeholder.Length > 0 && list.Count == 0) list.Add(placeholder);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title(title),
                _picker,
                UiKit.Buttons(
                    new Button
                    {
                        Content = buttonText,
                        Command = new RelayCommand(() =>
                        {
                            Accepted = true;
                            Close();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };
    }

    public bool Accepted { get; private set; }

    public string Value => _picker.SelectedItem as string ?? string.Empty;
}

/// <summary>
/// Notification centre (Cybersole.Ui.Views.Modals.NotificationView) — Clear / Delete /
/// Clock over the live notification list.
/// </summary>
public sealed class NotificationView : Window
{
    private readonly ListBox _items = new() { Height = 300 };
    private readonly List<string> _notifications = new();
    private readonly TextBlock _clock = UiKit.Status();

    /// <summary>"N Notifications", as the live popup's header reads (R336).</summary>
    private readonly TextBlock _caption = UiKit.Title("0 Notifications");

    /// <summary>Bound as <c>Clear</c>: empties the notification list.</summary>
    public ICommand Clear { get; }

    /// <summary>Bound as <c>Delete</c>: removes the selected notification.</summary>
    public ICommand Delete { get; }


    public NotificationView(AppServices services)
    {
        Title = "Notifications";
        Width = 560;
        Height = 520;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        services.Notify.Shown += (_, n) =>
        {
            _notifications.Insert(0, $"{DateTime.Now:HH:mm:ss}  [{n.Kind}]  {n.Title} — {n.Body}");
            Refresh();
        };

        _clock.Text = services.Clock.Current.ToString("u");

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                // R336: the live popup's header is "{count} Notifications" beside a single Clear button. It has no
                // clock row and no Delete button (the whole panel tree was read off the running build), so both are
                // gone; the clock field stays for the task engine, it just is not shown here.
                _caption,
                _items,
                UiKit.Buttons(
                    new Button
                    {
                        Content = "Clear",
                        Command = new RelayCommand(() =>
                        {
                            _notifications.Clear();
                            Refresh();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };

        Refresh();
    
        Clear = new RelayCommand(() =>
        {
            _notifications.Clear();
            Refresh();
        });

        Delete = new RelayCommand(() =>
        {
            if (_items.SelectedIndex < 0) return;
            _notifications.RemoveAt(_items.SelectedIndex);
            Refresh();
        });
}

    /// <summary>The popup's second empty line, verbatim from the running build (R336).</summary>
    public const string EmptyBody = "Your notifications will show up here";

    private void Refresh()
    {
        _caption.Text = $"{_notifications.Count} Notifications";
        _items.ItemsSource = _notifications.Count == 0
            ? new List<string> { Common.EmptyView.Headline, EmptyBody }
            : _notifications.ToList();
    }
}

/// <summary>
/// Toast (Cybersole.Ui.Views.Modals.DesktopNotification) — Close.
/// </summary>
public sealed class DesktopNotification : Window
{
    public DesktopNotification(string title, string body, int autoCloseMs = 6000)
    {
        Title = title;
        Width = 360;
        Height = 140;
        CanResize = false;
        ShowInTaskbar = false;
        WindowStartupLocation = WindowStartupLocation.Manual;
        Topmost = true;

        Content = new StackPanel
        {
            Margin = new Thickness(12),
            Spacing = 6,
            Children =
            {
                UiKit.Title(title),
                new TextBlock { Text = body, TextWrapping = TextWrapping.Wrap, Opacity = 0.85 },
                UiKit.Buttons(new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };

        if (autoCloseMs > 0)
        {
            _ = AutoCloseAsync(autoCloseMs);
        }
    }

    private async Task AutoCloseAsync(int ms)
    {
        await Task.Delay(ms).ConfigureAwait(true);
        try { Close(); }
        catch (Exception) { /* already closed */ }
    }
}

/// <summary>
/// User panel (Cybersole.Ui.Views.Modals.UserView) — LogOut / OpenUrl.
/// </summary>
public sealed class UserView : Window
{
    public const string DashboardUrl = "https://cybersole.io/dashboard";

    /// <summary>inferred: no image evidence (R337) — the live panel has the button, not the URL.</summary>
    public const string TermsUrl = "https://cybersole.io/terms";

    /// <summary>inferred: no image evidence (R337).</summary>
    public const string PrivacyUrl = "https://cybersole.io/privacy";

    /// <summary>The services this window acts on (bound as <c>LogOut</c> uses it).</summary>
    private AppServices? _services;

    /// <summary>
    /// Opens a link in the default browser (bound as <c>OpenUrl</c>, R355). The Terms of Service and Privacy Policy links
    /// on this panel call it; it returns false when the shell cannot start a browser.
    /// </summary>
    public static bool OpenUrl(string url)
    {
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = url,
                UseShellExecute = true,
            });
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>Signs the session out and closes the window (bound as <c>LogOut</c>).</summary>
    private bool LogOutCore()
    {
        if (_services is null) return false;

        _services.Auth.SignOut();
        Close();
        return true;
    }
    // R499: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>LogOut</c>; behaviour unchanged (was a method).</summary>
    public ICommand LogOut { get; }

    public UserView(AppServices services)
    {
        LogOut = new RelayCommand(() => LogOutCore());

        _services = services;
        Title = "Account";
        Width = 460;
        Height = 340;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var user = services.Auth.Claims;
        var status = UiKit.Status();

        // R337: laid out from the running build's profile panel:
        //   •  My License / [avatar] / name / email / [Dashboard ↗]
        //   ---------------------------------------------
        //   Terms of Service  •  Privacy Policy           [Log Out]
        var header = new TextBlock { Text = "\u2022  My License", FontSize = 12, Opacity = 0.8 };

        var avatar = new Border
        {
            Width = 64,
            Height = 64,
            CornerRadius = new CornerRadius(32),
            Background = Brushes.DimGray,
            HorizontalAlignment = HorizontalAlignment.Center,
            Child = new TextBlock
            {
                Text = "\u263A",
                FontSize = 28,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };

        var name = new TextBlock
        {
            Text = user?.Email is { Length: > 0 } mail ? mail.Split('@')[0] : "(signed out)",
            FontSize = 18,
            FontWeight = FontWeight.SemiBold,
            HorizontalAlignment = HorizontalAlignment.Center,
        };

        var email = new TextBlock
        {
            Text = user?.Email ?? string.Empty,
            FontSize = 11,
            Opacity = 0.6,
            HorizontalAlignment = HorizontalAlignment.Center,
        };

        var dashboard = new Button
        {
            Content = "Dashboard \u2197",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            Command = new RelayCommand(() => { OpenUrl(DashboardUrl); status.Text = "Opening " + DashboardUrl; }),
        };

        var terms = new Button { Content = "Terms of Service", Background = Brushes.Transparent, Padding = new Thickness(2, 0) };
        terms.Click += (_, _) => { OpenUrl(TermsUrl); status.Text = "Opening " + TermsUrl; };

        var privacy = new Button { Content = "Privacy Policy", Background = Brushes.Transparent, Padding = new Thickness(2, 0) };
        privacy.Click += (_, _) => { OpenUrl(PrivacyUrl); status.Text = "Opening " + PrivacyUrl; };

        // R213 kept an entry point for the signed-out case; the live panel only shows it when there is no session
        // (the signed-in panel in R337 has Dashboard / Terms / Privacy / Log Out and nothing else).
        var signIn = new Button
        {
            Content = "Sign in",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            IsVisible = user is null,
        };
        signIn.Click += (_, _) =>
        {
            var login = new Cybersole.Ui.Views.Auth.LoginControl(services);
            login.SignedIn += (_, _) => Close();
            status.Text = "Sign-in form opened.";
            if (Owner is Window host)
                _ = new Common.ViewHostModal("Login", login, 1536, 814).ShowDialog(host);
        };

        var logOut = new Button
        {
            Content = "Log Out",
            Background = Brushes.Crimson,
            Foreground = Brushes.White,
            Padding = new Thickness(10, 4),
            HorizontalAlignment = HorizontalAlignment.Right,
        };
        logOut.Click += (_, _) => LogOutCore();

        var footerLeft = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 6,
            VerticalAlignment = VerticalAlignment.Center,
            Children = { terms, new TextBlock { Text = "\u2022", Opacity = 0.6 }, privacy },
        };

        var footer = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        footer.Children.Add(footerLeft);
        Grid.SetColumn(logOut, 1);
        footer.Children.Add(logOut);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 10,
            Children =
            {
                header,
                avatar,
                name,
                email,
                dashboard,
                signIn,
                new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 4) },
                footer,
                status,
            },
        };
    }
}
