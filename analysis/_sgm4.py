import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('if (!_storeServices.Config.StoreGroups.Remove(_editing)) return false;',
              'if (!_storeServices.Config.Settings.StoreGroups.Remove(_editing)) return false;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('reads Settings.StoreGroups')
