import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
# repair lines 141..160 (1-based) back to the proxy-driver modal's closing
start = 140  # 0-based index of line 141
end = 160    # exclusive: up to but not including 0-based 160 (line 161 = '    }')
repaired = [
    '        BuildFooter(save,',
    '            DeleteButton(() =>',
    '            {',
    '                if (existing is null) return;',
    '                registry.RemoveConfig(existing);',
    '                services.Config.Save();',
    '            }));',
]
print('replacing:', [l.strip() for l in lines[start:end]][:3], '...', [l.strip() for l in lines[start:end]][-3:])
lines[start:end] = repaired
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('proxy-driver modal restored')
