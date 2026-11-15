import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Signs the session out and closes the window (bound as <c>LogOut</c>).</summary>'''
add = '''    /// <summary>
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

''' + anchor
assert anchor in t and 'public static bool OpenUrl' not in t
t = t.replace(anchor, add, 1)

t = t.replace('terms.Click += (_, _) => status.Text = "Opening " + TermsUrl;',
              'terms.Click += (_, _) => { OpenUrl(TermsUrl); status.Text = "Opening " + TermsUrl; };', 1)
t = t.replace('privacy.Click += (_, _) => status.Text = "Opening " + PrivacyUrl;',
              'privacy.Click += (_, _) => { OpenUrl(PrivacyUrl); status.Text = "Opening " + PrivacyUrl; };', 1)
t = t.replace('Command = new RelayCommand(() => status.Text = "Opening " + DashboardUrl),',
              'Command = new RelayCommand(() => { OpenUrl(DashboardUrl); status.Text = "Opening " + DashboardUrl; }),', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('UserView.OpenUrl added and wired to the three links')
