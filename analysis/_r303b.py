import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()

# replace the decorative button with a real command
old = '                UiKit.Button("Open tracking", () => Status("Opening tracking URL.")),'
new = '                UiKit.Button("Open tracking", () => OpenTracking()),'
assert old in t
t = t.replace(old, new, 1)

anchor = '    private void Status(string text)'
if anchor not in t:
    anchor = '    public void Refresh()'
add = '''    /// <summary>
    /// Opens the store's tracking page for the checkout on screen (bound as <c>OpenTracking</c>).
    ///
    /// <para>
    /// R303: the button used to write "Opening tracking URL." to the status bar and do nothing. It now opens the URL the
    /// flow captured (<c>CheckoutOutcome.TrackingUrl</c> — Shopify sets it from <c>order_status_url</c>), and says so
    /// when the store did not return one.
    /// </para>
    /// </summary>
    public bool OpenTracking()
    {
        if (_events.Count == 0) { Status("No checkout selected."); return false; }

        var current = _events[Math.Clamp(_index, 0, _events.Count - 1)];
        if (string.IsNullOrWhiteSpace(current.TrackingUrl))
        {
            Status("This checkout has no tracking URL.");
            return false;
        }

        if (TopLevel.GetTopLevel(this)?.Launcher is not { } launcher)
        {
            Status("This platform cannot open links.");
            return false;
        }

        launcher.LaunchUriAsync(new Uri(current.TrackingUrl!));
        Status("Opened " + current.TrackingUrl);
        return true;
    }

'''
t = t.replace(anchor, add + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('OpenTracking implemented')
