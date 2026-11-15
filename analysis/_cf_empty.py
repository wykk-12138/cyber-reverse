import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

# the Cloudflare page's empty state, verbatim (Settings.CloudflareSolvers.EmptySubtitle)
idx = t.index('public sealed class CloudflareSolversView')
head, tail = t[:idx], t[idx:]
old = '        var empty = UiKit.Empty(EmptyView.Headline);'
assert old in tail, 'empty state line not found'
tail = tail.replace(old,
    '        // R399: the Cloudflare page had the PROXIES empty line ("Add some proxies to get started"); the image\'s own\n'
    '        // sentence for this page is Settings.CloudflareSolvers.EmptySubtitle.\n'
    '        var empty = UiKit.Empty(EmptyView.Headline, "Add a Cloudflare provider to get started");', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(head + tail)
print('cloudflare empty subtitle fixed')
