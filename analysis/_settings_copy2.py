import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''        ["Text"] = '''
i = t.index('public static readonly IReadOnlyDictionary<string, string> Copy')
j = t.index('    };', i)
add = '''
        ["SizesDeleteConfirmMessage"] = "Are you sure you want to delete {0} sizes?\\nYou cannot undo this action.",   // Settings.Sizes.DeleteConfirm.MessageFormat
        ["StoresDeleteConfirmMessage"] = "Are you sure you want to delete {0} presets?\\nYou cannot undo this action.",   // Settings.Stores.DeleteConfirm.MessageFormat
'''
t = t[:j] + add + t[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('two delete-confirm messages added')
