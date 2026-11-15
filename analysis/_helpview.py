import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

# HelpView.OpenUrl: the local Open(url) becomes the bound member
old = '''        void Open(string url)
        {
            try
            {
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo'''
new = '''        void Open(string url) => OpenUrl(url);

        void OpenLegacy(string url)
        {
            try
            {
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo'''
assert old in t
t = t.replace(old, new, 1)

# declare the bound member on HelpView
anchor = '''    public static IReadOnlyList<Cybersole.Stores.Flows.ErrorCatalog.Entry> Filter(string? query)'''
add = '''    /// <summary>
    /// Opens one of the help links in the default browser (bound as <c>OpenUrl</c>, R346). The two URLs the page offers
    /// are <see cref="CommunityUrl"/> and <see cref="DocsUrl"/>; this is the operation the binding table names.
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
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('HelpView.OpenUrl added')
