import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGroupView.cs"
t = io.open(p, encoding='utf-8').read()
start = t.index('    /// <summary>\n    /// Removes the selected proxy group')
end = t.index('    /// <summary>Closes the hosting dialog', start)
t = t[:start] + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('bad Delete reverted')
