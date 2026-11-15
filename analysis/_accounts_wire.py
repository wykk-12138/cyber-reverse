import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()

# 1) the empty-search line: use the constant recovered this session
old1 = '                Text = "No stores matched your search",'
if old1 in t:
    t = t.replace(old1, '                Text = NoResultsSubtitle,', 1)
    print('store-search empty line wired')

# 2) the group-pane footer: prefer the Accounts.GroupsLoaded* family (the pane counts GROUPS, not accounts)
old2 = '''            Text = LoadedCaption(group.Accounts.Count),'''
if old2 in t:
    t = t.replace(old2, '''            Text = GroupsLoaded(_doc.AccountGroups.Count),''', 1)
    print('group pane footer wired to GroupsLoaded')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
