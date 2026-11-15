import io

def table(pairs, anchor_file, anchor_class, key_comment):
    lines = ['', "    // ------------------------------------------------ copy from the image's locale (%s)" % key_comment, '    //',
             "    // Verbatim from the string table; same shape as the other pages' copy tables.",
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
    t = io.open(anchor_file, encoding='utf-8').read()
    i = t.index(anchor_class)
    brace = t.index('{', i)
    line_end = t.index('\n', brace) + 1
    assert 'IReadOnlyDictionary<string, string> Copy' not in t[line_end:line_end + 4000], anchor_class
    t = t[:line_end] + block + t[line_end:]
    io.open(anchor_file, 'w', encoding='utf-8', newline='').write(t)
    print('captured', len(pairs), 'strings into', anchor_class)

monitor = [
 ("Empty", "Waiting for monitor entries", "Monitor.Empty"),
 ("NoResultsTitle", "No results", "Monitor.Empty.NoResults.Title"),
 ("NothingSubtitle", "New products and restocks will appear here", "Monitor.Empty.Nothing.Subtitle"),
 ("SearchPlaceholder", "Search feed", "Monitor.SearchPlaceholder"),
 ("SizesAvailable", "Available sizes", "Monitor.Sizes.Available"),
 ("SizesNone", "No available sizes", "Monitor.Sizes.None"),
 ("TabFeed", "Monitor Feed", "Monitor.Tab.Feed"),
]
table(monitor, r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Monitor\MonitorView.cs", 'public sealed class MonitorView', 'R415')

checkout = [
 ("OrderFormat", "Order {0}", "Checkout.OrderFormat"),
 ("OutForDelivery", "Out for delivery", "Checkout.OutForDelivery"),
 ("Order", "Order", "Checkout.Order"),
]
import os
cands = []
for dp, _d, fns in os.walk(r"D:\projects\cyber-reverse\replica\src"):
    for fn in fns:
        if fn.endswith('.cs'):
            p = os.path.join(dp, fn)
            if 'class CheckoutView' in io.open(p, encoding='utf-8', errors='replace').read():
                cands.append(p)
print('CheckoutView file:', cands[:1])
