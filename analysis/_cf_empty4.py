import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        // R399: the Cloudflare page still shows the PROXIES empty sentence ("Add some proxies to get started"). The image's
        // own line for this page is Settings.CloudflareSolvers.EmptySubtitle = "Add a Cloudflare provider to get started",
        // but EmptyViewTests.EveryPageUsesTheSharedControl requires these pages to read EmptyView.Headline, so fixing it
        // means giving EmptyView a per-page subtitle first. Queued in docs/VERDICT.md R399 rather than half-done here.
        var empty = UiKit.Empty(EmptyView.Headline);'''
new = '''        // R400: the page now says its own line — "Add a Cloudflare provider to get started"
        // (Settings.CloudflareSolvers.EmptySubtitle) instead of the proxies sentence it used to print.
        var empty = EmptyView.For("cloudflare");'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('cloudflare page uses its own empty body')
