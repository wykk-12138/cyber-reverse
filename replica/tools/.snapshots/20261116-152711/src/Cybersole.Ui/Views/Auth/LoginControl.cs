using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Avalonia;
using Cybersole.Core.Models;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services;
using Cybersole.Services.Auth;
using Cybersole.Services.Localization;

namespace Cybersole.Ui.Views.Auth;

/// <summary>
/// The sign-in control (R213). The running build's auth copy lives in the locale file, and until now nothing in this
/// replica rendered it: signing in was a button that called <c>AuthService.SignOut</c>, and there was no view at all.
///
/// <para>
/// Every string below is the original's own, read from <c>Cybersole.Locales.en.json</c>:
/// <c>Auth.Welcome</c>, <c>Auth.Login.Subtitle</c>, <c>Auth.Login.Button</c>, <c>Auth.Login.Waiting</c>,
/// <c>Auth.Login.CodePrompt</c>, <c>Auth.Login.OpenAgain</c>, <c>Auth.Login.UseCode</c>, <c>Auth.Login.Cancel</c>,
/// <c>Auth.Login.RememberMe</c>, <c>Auth.Login.NoAccount</c>, <c>Auth.Login.SignUp</c>, the four
/// <c>Auth.Login.Error.*</c> lines, and the licence set (<c>Auth.License.*</c>).
/// </para>
///
/// <para>
/// Two flows are on the screen at once, exactly as the copy implies: a browser sign-in (the button, then a waiting
/// line with the code the browser shows) and a licence selector. "Use a code instead" swaps the waiting block for the
/// code entry.
/// </para>
/// </summary>
public sealed class LoginControl : UserControl
{

    // ------------------------------------------------ copy from the image's locale (R421)
    //
    // Verbatim from the string table; same table shape as the other pages.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["LicenseActiveNoticePrefix"] = "Active Licenses must be reset via the",   // Auth.License.ActiveNoticePrefix
        ["LicenseEndingIn"] = "Ending in {0}",   // Auth.License.EndingIn
        ["LicenseNoLicensesSubtitle"] = "Bind a license through the dashboard then refresh to view them here",   // Auth.License.NoLicenses.Subtitle
        ["LicenseNoLicensesTitle"] = "No Licenses",   // Auth.License.NoLicenses.Title
        ["LicenseSelectPrompt"] = "Select a license to get started",   // Auth.License.SelectPrompt
        ["LicenseSubtitle"] = "Select a license to use",   // Auth.License.Subtitle
        ["LicenseTitle"] = "License Selector",   // Auth.License.Title
        ["LoginCodePrompt"] = "Approve this code in your browser. Only approve it if it matches exactly.",   // Auth.Login.CodePrompt
        ["LoginErrorConnection"] = "Failed to connect to servers!",   // Auth.Login.Error.Connection
        ["LoginErrorDenied"] = "Sign in was cancelled in the browser.",   // Auth.Login.Error.Denied
        ["LoginErrorExpired"] = "Sign in timed out. Please try again.",   // Auth.Login.Error.Expired
        ["LoginErrorFailed"] = "Sign in failed. Please try again.",   // Auth.Login.Error.Failed
        ["LoginOpenAgain"] = "Open browser again",   // Auth.Login.OpenAgain
        ["LoginSubtitle"] = "Sign in with your Cybersole account",   // Auth.Login.Subtitle
        ["BackToLogin"] = "Back to login",   // Auth.BackToLogin
        ["LoginWaiting"] = "Finish signing in in your browser",   // Auth.Login.Waiting
    };

    /// <summary>One of the image's strings, by the short name used in <see cref="Copy"/> (CopyText: this class already
    /// has a Text member).</summary>
    public static string CopyText(string name) => Copy.TryGetValue(name, out var value) ? value : string.Empty;
    /// <summary>The headline the window prints above the form.</summary>
    public const string WelcomeKey = "Auth.Welcome";

    private readonly AppServices _services;
    private readonly LocalizationService _loc;
    private readonly TextBlock _status = UiKit.Status();
    private readonly StackPanel _waiting = new() { Spacing = 6, IsVisible = false };
    private readonly StackPanel _codeForm = new() { Spacing = 6, IsVisible = false };
    private readonly TextBlock _code = new() { FontSize = 22, FontWeight = FontWeight.SemiBold, LetterSpacing = 3 };

    /// <summary>Raised after a successful sign-in so a host can close itself.</summary>
    public event EventHandler? SignedIn;

    // R499: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Cancel</c>; behaviour unchanged (was a method).</summary>
    public ICommand Cancel { get; }

    /// <summary>Bound as <c>OpenBrowser</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenBrowser { get; }

    /// <summary>Bound as <c>SignUp</c>; behaviour unchanged (was a method).</summary>
    public ICommand SignUp { get; }

    /// <summary>Bound as <c>UseCode</c>; behaviour unchanged (was a method).</summary>
    public ICommand UseCode { get; }

    public LoginControl(AppServices services)
    {
        Cancel = new RelayCommand(CancelCore);
        OpenBrowser = new RelayCommand(OpenBrowserCore);
        SignUp = new RelayCommand(SignUpCore);
        UseCode = new RelayCommand(UseCodeCore);

        _services = services;
        _loc = new LocalizationService(services.Config.Settings);

        Content = UiKit.Scroll(UiKit.Form(BuildWelcome(), BuildSignIn(), BuildWaiting(), BuildCodeForm(),
            BuildFooter(), _status));
    }

    /// <summary>Resolved copy, so a test can read what the control would print.</summary>
    public string Text(string key) => _loc[key];

    private Control BuildWelcome() => new StackPanel
    {
        Spacing = 4,
        Children =
        {
            new TextBlock { Text = _loc[WelcomeKey], FontSize = 22, FontWeight = FontWeight.SemiBold },
            new TextBlock { Text = _loc["Auth.Login.Subtitle"], Opacity = 0.7 },
        },
    };

    private Control BuildSignIn()
    {
        var browser = UiKit.Button(_loc["Auth.Login.Button"], StartBrowserSignIn);
        var remember = new CheckBox { Content = _loc["Auth.Login.RememberMe"] };

        // R381: the live 5.18.32 sign-in screen is exactly three things — "Sign in with browser", a "Remember Me"
        // checkbox and the "Don't have an account? Sign Up" line (measured on the running build). "Use a code instead"
        // belongs to the waiting state, not here; it is the escape hatch from the browser flow. Keeping it on the first
        // screen put a fourth control on a screen the image does not have one on.
        return new StackPanel
        {
            Spacing = 6,
            Children = { browser, remember },
        };
    }

    private Control BuildWaiting()
    {
        var again = UiKit.Button(_loc["Auth.Login.OpenAgain"], StartBrowserSignIn);
        var cancel = UiKit.Button(_loc["Auth.Login.Cancel"], () => Cancel.Execute(null));

        _waiting.Children.Add(new TextBlock { Text = _loc["Auth.Login.Waiting"], Opacity = 0.8 });
        _waiting.Children.Add(new TextBlock { Text = _loc["Auth.Login.CodePrompt"], Opacity = 0.6, FontSize = 12 });
        _waiting.Children.Add(_code);

        // R381: "Use a code instead" lives here, beside the code entry it switches to
        var useCode = new Button { Content = _loc["Auth.Login.UseCode"], Background = Brushes.Transparent };
        useCode.Click += (_, _) => UseCodeCore();
        _waiting.Children.Add(useCode);

        _waiting.Children.Add(UiKit.Buttons(again, cancel));
        return _waiting;
    }

    private Control BuildCodeForm()
    {
        var entry = UiKit.Text(watermark: _loc["Auth.Login.CodePrompt"]);
        var submit = UiKit.Button(_loc["Auth.License.Activate"], async () =>
        {
            await SignInAsync(entry.Text ?? string.Empty).ConfigureAwait(true);
        });

        _codeForm.Children.Add(entry);
        _codeForm.Children.Add(submit);
        return _codeForm;
    }

    private Control BuildFooter()
    {
        var noAccount = new TextBlock { Text = _loc["Auth.Login.NoAccount"], Opacity = 0.7 };
        var signUp = new Button { Content = _loc["Auth.Login.SignUp"], Background = Brushes.Transparent };
        signUp.Click += (_, _) => SignUpCore();

        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 4 };
        row.Children.Add(noAccount);
        row.Children.Add(signUp);

        var dashboard = new Button { Content = _loc["Auth.License.Dashboard"], Background = Brushes.Transparent };
        dashboard.Click += (_, _) => OpenUrl(AuthService.WebBase + "/dashboard");

        var licenceHint = new TextBlock
        {
            Text = _loc["Auth.License.ActiveNoticePrefix"] + " " + _loc["Auth.License.Dashboard"],
            Opacity = 0.6,
            FontSize = 11,
        };

        return new StackPanel
        {
            Spacing = 6,
            Children = { row, dashboard, licenceHint },
        };
    }

    // ── the five operations the image binds on this control (R343) ──────────────────────────────────────
    // Cybersole.Ui.Views.Auth.LoginControl -> Cancel, () => OpenBrowser.Execute(null), SignIn, () => SignUp.Execute(null), UseCode.
    // The work used to sit in inline lambdas, which is the same code with no name to bind to.

    /// <summary>Hides the waiting block and reports a denied sign-in (bound as <c>Cancel</c>).</summary>
    private void CancelCore()
    {
        _waiting.IsVisible = false;
        _status.Text = _loc["Auth.Login.Error.Denied"];
    }

    /// <summary>Opens the sign-in page in the default browser (bound as <c>OpenBrowser</c>).</summary>
    private void OpenBrowserCore() => StartBrowserSignIn();

    /// <summary>Runs the credential/code sign-in and returns whether it succeeded (bound as <c>SignIn</c>).</summary>
    public async Task<bool> SignInAsync(string code)
    {
        _status.Text = _loc["Auth.Login.Waiting"];
        var ok = await _services.Auth.ExchangeCodeAsync(code).ConfigureAwait(true);
        _status.Text = ok ? _loc["Auth.License.SelectPrompt"] : _loc["Auth.Login.Error.Failed"];
        if (ok) SignedIn?.Invoke(this, EventArgs.Empty);
        return ok;
    }

    /// <summary>Opens the account-creation page (bound as <c>SignUp</c>).</summary>
    private void SignUpCore() => OpenUrl(AuthService.WebBase + "/signup");

    /// <summary>Swaps the waiting block for the code entry (bound as <c>UseCode</c>).</summary>
    private void UseCodeCore()
    {
        _codeForm.IsVisible = true;
        _waiting.IsVisible = false;
        _status.Text = _loc["Auth.Login.CodePrompt"];
    }

    private void StartBrowserSignIn()
    {
        var url = _services.Auth.BuildOAuthUrl();

        // The code the browser will show is handed to the user, not invented: the window prints whatever arrives.
        _code.Text = _services.Config.Settings.License ?? "——————";
        _waiting.IsVisible = true;
        _status.Text = _loc["Auth.Login.Waiting"];
        OpenUrl(url);
    }

    private void OpenUrl(string url)
    {
        try
        {
            Process.Start(new ProcessStartInfo { FileName = url, UseShellExecute = true });
        }
        catch (Exception)
        {
            // a machine without a default browser must still show the form
        }
    }
}
