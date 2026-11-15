import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('                Text = NoResultsSubtitle,', '                Text = "No stores matched your search",', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('stores empty line restored (different empty state than the accounts one)')
