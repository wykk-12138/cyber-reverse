using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Cybersole.Services;
using Cybersole.Services.Localization;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R213: <c>LoginControl</c> — the sign-in view the window has copy for and this replica had no control for.
/// The assertions read the locale, because the copy is the evidence: every line on screen is a key in
/// <c>Cybersole.Locales.en.json</c>.
/// </summary>
public sealed class LoginControlTests
{
    private readonly ITestOutputHelper _out;
    public LoginControlTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Ui(string relative) =>
        File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Views",
            relative.Replace('/', Path.DirectorySeparatorChar)));

    [Fact]
    public void EveryLineOnTheFormIsAKeyTheOriginalShips()
    {
        var en = LocalizationService.For("en");

        var keys = new[]
        {
            "Auth.Welcome", "Auth.Login.Subtitle", "Auth.Login.Button", "Auth.Login.Waiting",
            "Auth.Login.CodePrompt", "Auth.Login.OpenAgain", "Auth.Login.UseCode", "Auth.Login.Cancel",
            "Auth.Login.RememberMe", "Auth.Login.NoAccount", "Auth.Login.SignUp",
            "Auth.Login.Error.Denied", "Auth.Login.Error.Expired", "Auth.Login.Error.Failed",
            "Auth.Login.Error.Connection",
            "Auth.License.Title", "Auth.License.Subtitle", "Auth.License.SelectPrompt", "Auth.License.Activate",
            "Auth.License.Dashboard", "Auth.License.NoLicenses.Title", "Auth.License.NoLicenses.Subtitle",
        };

        foreach (var key in keys)
        {
            Assert.True(en.ContainsKey(key), "locale is missing " + key);
            _out.WriteLine($"{key} = {en[key]}");
        }

        Assert.Equal("Welcome to Cybersole 5.0", en["Auth.Welcome"]);
        Assert.Equal("Sign in with browser", en["Auth.Login.Button"]);
    }

    [Fact]
    public void TheControlRendersThoseKeysAndNothingInvented()
    {
        var source = Ui("Auth/LoginControl.cs");
        var en = LocalizationService.For("en");

        // every Auth.* key the control mentions must exist in the locale
        var used = Regex.Matches(source, "\"(Auth\\.[A-Za-z0-9_.]+)\"")
            .Select(m => m.Groups[1].Value)
            .Distinct()
            .OrderBy(k => k, System.StringComparer.Ordinal)
            .ToList();

        _out.WriteLine("keys used: " + string.Join(", ", used));
        Assert.NotEmpty(used);

        foreach (var key in used)
            Assert.True(en.ContainsKey(key), "LoginControl uses a key the original does not ship: " + key);

        // the welcome headline comes from the constant, not a copy of the string
        Assert.Contains("public const string WelcomeKey = \"Auth.Welcome\";", source);
        Assert.DoesNotContain("\"Welcome to Cybersole 5.0\"", source);
    }

    [Fact]
    public void ItHasAnEntryPointInTheAccountWindow()
    {
        var modal = Ui("Modals/CommonModals.cs");

        Assert.Contains("new Cybersole.Ui.Views.Auth.LoginControl(services)", modal);
        // R217: the host is the measured "Login" window at 1536x814, not a small "Sign in" card
        Assert.Contains("ViewHostModal(\"Login\", login, 1536, 814)", modal);
    }

    /// <summary>
    /// R343: the five operations the binding table binds on this control exist as methods, not as inline lambdas.
    ///
    /// <para>
    /// <c>Cybersole.Ui.Views.Auth.LoginControl</c> binds Cancel, OpenBrowser, SignIn, SignUp and UseCode. The replica did
    /// all of it inside click handlers, which is the same behaviour with nothing to bind to — the same correction R239
    /// made on NotificationsView. SignIn is async because it exchanges the code with the auth service, so it is checked
    /// by name here and exercised through the code form.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFiveBoundOperationsExistAsMembers()
    {
        var type = typeof(Cybersole.Ui.Views.Auth.LoginControl);
        var names = type.GetMembers().Select(m => m.Name).ToList();

        foreach (var bound in new[] { "Cancel", "OpenBrowser", "SignUp", "UseCode" })
            Assert.Contains(bound, names);

        Assert.Contains("SignInAsync", names);
        Assert.Equal(typeof(System.Threading.Tasks.Task<bool>), type.GetMethod("SignInAsync")!.ReturnType);
    }
}
