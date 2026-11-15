import io

auth = [
 ("LicenseActiveNoticePrefix", "Active Licenses must be reset via the", "Auth.License.ActiveNoticePrefix"),
 ("LicenseEndingIn", "Ending in {0}", "Auth.License.EndingIn"),
 ("LicenseNoLicensesSubtitle", "Bind a license through the dashboard then refresh to view them here", "Auth.License.NoLicenses.Subtitle"),
 ("LicenseNoLicensesTitle", "No Licenses", "Auth.License.NoLicenses.Title"),
 ("LicenseSelectPrompt", "Select a license to get started", "Auth.License.SelectPrompt"),
 ("LicenseSubtitle", "Select a license to use", "Auth.License.Subtitle"),
 ("LicenseTitle", "License Selector", "Auth.License.Title"),
 ("LoginCodePrompt", "Approve this code in your browser. Only approve it if it matches exactly.", "Auth.Login.CodePrompt"),
 ("LoginErrorConnection", "Failed to connect to servers!", "Auth.Login.Error.Connection"),
 ("LoginErrorDenied", "Sign in was cancelled in the browser.", "Auth.Login.Error.Denied"),
 ("LoginErrorExpired", "Sign in timed out. Please try again.", "Auth.Login.Error.Expired"),
 ("LoginErrorFailed", "Sign in failed. Please try again.", "Auth.Login.Error.Failed"),
 ("LoginOpenAgain", "Open browser again", "Auth.Login.OpenAgain"),
 ("LoginSubtitle", "Sign in with your Cybersole account", "Auth.Login.Subtitle"),
 ("LoginWaiting", "Finish signing in in your browser", "Auth.Login.Waiting"),
]

history = [
 ("Empty", "No history entries", "HistoryWindow.Empty"),
 ("EmptyNoMatch", "No recent runs match your filter!", "HistoryWindow.Empty.NoMatch"),
 ("EmptyNoRuns", "Smart Action hasn't been triggered yet", "HistoryWindow.Empty.NoRuns"),
 ("EmptySubtitle", "Run history will appear here", "HistoryWindow.Empty.Subtitle"),
 ("EmptyInput", "Empty input", "HistoryWindow.EmptyInput"),
 ("HoverTip", "Hover over each step to view more details", "HistoryWindow.HoverTip"),
 ("ResultSuccess", "The Smart Action completed successfully!", "HistoryWindow.Result.Success"),
 ("SearchPlaceholder", "Search history", "HistoryWindow.SearchPlaceholder"),
]

def table(pairs, path, cls, note):
    lines = ['', "    // ------------------------------------------------ copy from the image's locale (%s)" % note, '    //',
             "    // Verbatim from the string table; same table shape as the other pages.",
             "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
             '    {']
    for name, value, key in pairs:
        esc = value.replace('\\', '\\\\').replace('"', '\\"')
        lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
    lines.append('    };')
    lines.append('')
    lines.append("    /// <summary>One of the image's strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
    lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
    lines.append('')
    block = '\n'.join(lines)
    t = io.open(path, encoding='utf-8').read()
    i = t.index(cls)
    brace = t.index('{', i); line_end = t.index('\n', brace) + 1
    assert 'IReadOnlyDictionary<string, string> Copy' not in t[line_end:line_end + 4000], cls
    io.open(path, 'w', encoding='utf-8', newline='').write(t[:line_end] + block + t[line_end:])
    print('captured', len(pairs), 'into', cls)

table(auth, r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs", 'public sealed class LoginControl', 'R421')
table(history, r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs", 'public sealed class HistoryWindow', 'R421')
