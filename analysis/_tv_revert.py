import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

start = t.index('    /// <summary>\n    /// Copies the product URL of the first selected task')
end = t.index('    /// <summary>Moves the group picker to the next group')
removed = t[start:end]
t = t[:start] + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CopyUrl removed (%d chars) — the URL source does not exist yet' % len(removed))
