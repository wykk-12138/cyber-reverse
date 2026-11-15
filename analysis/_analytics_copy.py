import io
pairs = [
 ("OrderFormat", "Order {0}", "Checkout.OrderFormat"),
 ("OutForDelivery", "Out for delivery", "Checkout.OutForDelivery"),
 ("ReleaseAddTasks", "Add Tasks", "Release.AddTasks"),
 ("ReleaseEmptyCheckBack", "Check back later", "Release.Empty.CheckBack"),
]
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
lines = ['', "    // ------------------------------------------------ copy from the image's locale (R415)",
         '    //',
         '    // Checkout.OrderFormat / Checkout.OutForDelivery and Release.AddTasks / Release.Empty.CheckBack: the words the',
         '    // analytics pages use, which had no counterpart anywhere in the source.',
         '    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)',
         '    {']
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's analytics strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
block = '\n'.join(lines)
i = t.index('public sealed class CheckoutView')
brace = t.index('{', i); line_end = t.index('\n', brace) + 1
assert 'IReadOnlyDictionary<string, string> Copy' not in t[line_end:line_end + 4000]
t = t[:line_end] + block + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('4 analytics strings captured on CheckoutView')
