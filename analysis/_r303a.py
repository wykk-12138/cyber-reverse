import io
# 1) CheckoutEvent gains an optional TrackingUrl
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\EventBus.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>When the checkout completed — used to order the analytics feeds.</summary>
    public DateTime At { get; init; } = DateTime.UtcNow;'''
new = '''    /// <summary>When the checkout completed — used to order the analytics feeds.</summary>
    public DateTime At { get; init; } = DateTime.UtcNow;

    /// <summary>
    /// Where the store's tracking page for this checkout lives, when the flow got one back (R303: CheckoutView's
    /// "Open tracking" button wrote a sentence and nothing else, because this event carried no URL at all).
    /// </summary>
    public string? TrackingUrl { get; init; }'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('CheckoutEvent.TrackingUrl added')

# 2) TaskEngine passes it through
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Services\TaskEngine.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''            outcome.Success, outcome.OrderNumber, profile.Name));'''
new2 = '''            outcome.Success, outcome.OrderNumber, profile.Name)
        {
            TrackingUrl = outcome.TrackingUrl,
        });'''
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2, 1))
print('TaskEngine passes TrackingUrl into the event')
