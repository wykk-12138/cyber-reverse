import io
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs"
t2 = io.open(p2, encoding='utf-8').read()
old = '\t\tGrid.SetColumn(selectAll, 0);\n\t\tgrid.Children.Add(selectAll);'
new = '''\t\t// R319: header cells are described as ElementCell, so the column rule is data instead of a repeated call.
\t\tforeach (var cell in new[]
\t\t         {
\t\t             new ElementCell("select-all", selectAll, 0),
\t\t             new ElementCell("header-actions", _headerActions, 6),
\t\t         })
\t\t{
\t\t\tif (cell.Content is not Control control) continue;
\t\t\tGrid.SetColumn(control, cell.Column);
\t\t\tGrid.SetColumnSpan(control, cell.ColumnSpan);
\t\t}

\t\tGrid.SetColumn(selectAll, 0);
\t\tgrid.Children.Add(selectAll);'''
assert old in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
print('TaskGrid header placement now uses ElementCell')
