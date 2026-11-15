import io
# TaskGrid: derive the header row from a single array so the order is data
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs"
t = io.open(p, encoding='utf-8').read()
old = '''\t\tgrid.Children.Add(HeaderButton("Site", TaskColumn.Site, 1));
\t\tgrid.Children.Add(HeaderButton("Product", TaskColumn.Product, 2));
\t\tgrid.Children.Add(HeaderButton("Profile", TaskColumn.Profile, 3));
\t\tgrid.Children.Add(HeaderButton("Proxies", TaskColumn.Proxies, 4));
\t\tgrid.Children.Add(HeaderButton("Status", TaskColumn.Status, 5));'''
new = '''\t\t// R333: the header row comes from one array, so the order the live page shows (R331) is data and testable.
\t\tfor (var i = 0; i < Headers.Length; i++)
\t\t\tgrid.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));'''
assert old in t
t = t.replace(old, new, 1)

anchor = '\tprivate Control Build()'
add = '''\t/// <summary>The sortable columns, in the order the live page shows them (R331).</summary>
\tinternal static readonly string[] Headers = { "Site", "Product", "Profile", "Proxies", "Status" };

\t/// <summary>The same columns as sort keys, positionally aligned with <see cref="Headers"/>.</summary>
\tprivate static readonly TaskColumn[] HeaderColumns =
\t{
\t\tTaskColumn.Site, TaskColumn.Product, TaskColumn.Profile, TaskColumn.Proxies, TaskColumn.Status,
\t};

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskGrid: Headers array introduced')

# ProxyGrid: same treatment
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGrid.cs"
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''        header.Children.Add(HeaderButton("IP", ProxyColumn.Ip, 1));
        header.Children.Add(HeaderButton("Port", ProxyColumn.Port, 2));
        header.Children.Add(HeaderButton("Username", ProxyColumn.Username, 3));
        header.Children.Add(HeaderButton("Status", ProxyColumn.Status, 4));'''
new2 = '''        // R333: one array drives the row, so the order the live page shows (R332) is data and testable.
        for (var i = 0; i < Headers.Length; i++)
            header.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));'''
assert old2 in t2
t2 = t2.replace(old2, new2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ProxyGrid: header loop introduced')
