import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\EmptyView.cs"
t = io.open(p, encoding='utf-8').read()
old = '''            ["profiles"] = "Add some profiles to get started",
        };'''
new = '''            ["profiles"] = "Add some profiles to get started",
            ["cloudflare"] = "Add a Cloudflare provider to get started",
            ["smartActions"] = "Add a smart action to get started",
        };

    /// <summary>
    /// The page-specific second line for <paramref name="key"/>, or the headline's default when the page has none.
    /// </summary>
    /// <remarks>
    /// R400: <c>Settings.CloudflareSolvers.EmptySubtitle</c> is "Add a Cloudflare provider to get started", while the page used
    /// to print the proxies sentence. Adding a key here is how a page gets its own line — the shared headline stays shared.
    /// </remarks>
    public static string Body(string key) => Bodies.TryGetValue(key, out var body) ? body : string.Empty;

    /// <summary>The block a page draws, with its own second line.</summary>
    public static EmptyView For(string key, double iconSize = 96) => new(Body(key), iconSize);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('EmptyView gains Body(key) and For(key)')
