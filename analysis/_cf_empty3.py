import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        // R399: the Cloudflare page had the PROXIES empty line ("Add some proxies to get started"); the image's own
        // sentence for this page is Settings.CloudflareSolvers.EmptySubtitle.
        var empty = UiKit.Empty("Add a Cloudflare provider to get started");'''
new = '''        // R399: the Cloudflare page still shows the PROXIES empty sentence ("Add some proxies to get started"). The image's
        // own line for this page is Settings.CloudflareSolvers.EmptySubtitle = "Add a Cloudflare provider to get started",
        // but EmptyViewTests.EveryPageUsesTheSharedControl requires these pages to read EmptyView.Headline, so fixing it
        // means giving EmptyView a per-page subtitle first. Queued in docs/VERDICT.md R399 rather than half-done here.
        var empty = UiKit.Empty(EmptyView.Headline);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('reverted; the guard needs an EmptyView subtitle API first')
