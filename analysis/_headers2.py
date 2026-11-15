import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGrid.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly IList<Proxy> _rows;'''
add = '''    /// <summary>The sortable columns, in the order the live page shows them (R332).</summary>
    internal static readonly string[] Headers = { "IP", "Port", "Username", "Status" };

    /// <summary>The same columns as sort keys, positionally aligned with <see cref="Headers"/>.</summary>
    private static readonly ProxyColumn[] HeaderColumns =
    {
        ProxyColumn.Ip, ProxyColumn.Port, ProxyColumn.Username, ProxyColumn.Status,
    };

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ProxyGrid: Headers declared')
