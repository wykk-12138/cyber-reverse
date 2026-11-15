import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\DeadButtonTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '        "Views/Analytics/AnalyticsViews.cs:Open tracking",\n'
assert old in t
new = '        // R303: "Open tracking" was here — it wrote a sentence and nothing else. It now opens\n' \
      '        // CheckoutEvent.TrackingUrl through the platform launcher, so it is no longer a dead button.\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('dead-button ledger updated')
