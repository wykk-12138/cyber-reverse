import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Proxies.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public TimeSpans? UsageExpiry { get; set; }'''
add = '''    public TimeSpans? UsageExpiry { get; set; }

    /// <summary>
    /// The allowance window length, persisted beside <see cref="UsageExpiry"/> as <c>usagePeriod</c>.
    /// </summary>
    /// <remarks>
    /// R389: R54 concluded from the binding table that "there is no separate period field" — the XAML does bind only
    /// <c>UsageExpiry</c>. A real 5.18.32 backup writes BOTH <c>usagePeriod</c> and <c>usageExpiry</c> on every proxy group
    /// (<c>Backups/Backup 14 Nov 08h01m.cyb</c>), so the field is persisted even though nothing in the markup edits it.
    /// Persistence evidence outranks a binding list; both stay.
    /// </remarks>
    public TimeSpans? UsagePeriod { get; set; }'''
assert anchor in t and 'public TimeSpans? UsagePeriod' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ProxyGroup.UsagePeriod added')
