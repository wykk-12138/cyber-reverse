"""R1285: honour the image's read-only Type in the provider creator modal.

The image's CaptchaProvider.Type has a getter and no setter, so an existing row cannot change its source; only a new
row picks one. The modal used to assign target.Type on save, which is exactly what the missing setter forbids.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Ui/Views/Settings/Modals/SettingsModals.cs'
text = io.open(P, encoding='utf-8').read()

# 1. the type combo is fixed once the row exists
old_row = '        Body.Children.Add(UiKit.Row("Type", type));'
new_row = ('        // R1285: Type has no setter in the image (1432159DC getter, no setter), so an existing row\n'
           '        // cannot change its source — the combo is read-only when editing.\n'
           '        if (existing is not null) type.IsEnabled = false;\n'
           '        Body.Children.Add(UiKit.Row("Type", type));')
if old_row not in text:
    raise SystemExit('combo row anchor missing')
text = text.replace(old_row, new_row)

# 2. save builds a new row with the chosen Type instead of writing to an existing one
old_save = ('        var save = SaveButton(() =>\n'
            '        {\n'
            '            target.Type = drivers.Count > 0 && type.SelectedIndex >= 0\n'
            '                ? drivers.ElementAt(type.SelectedIndex).Type\n'
            '                : target.Type;\n'
            '            target.Name = string.IsNullOrWhiteSpace(name.Text) ? target.Type : name.Text!;\n'
            '            target.ApiKey = apiKey.Text;\n'
            '            if (UiKit.TryReadInt(concurrency.Text, out var c)) target.Concurrency = c;\n'
            '            if (UiKit.TryReadInt(priority.Text, out var p)) target.Priority = p;\n'
            '            target.Enabled = enabled.IsChecked == true;\n'
            '\n'
            '            if (existing is null) registry.AddConfig(target);')

new_save = ('        var save = SaveButton(() =>\n'
            '        {\n'
            '            // R1285: only creation picks a Type. An existing row keeps the source it was opened with,\n'
            '            // because the image gives that property a getter and no setter.\n'
            '            var row = existing is null\n'
            '                ? new CaptchaProviderConfig\n'
            '                {\n'
            '                    Type = drivers.Count > 0 && type.SelectedIndex >= 0\n'
            '                        ? drivers.ElementAt(type.SelectedIndex).Type\n'
            '                        : target.Type,\n'
            '                }\n'
            '                : target;\n'
            '\n'
            '            row.Name = string.IsNullOrWhiteSpace(name.Text) ? row.Type : name.Text!;\n'
            '            row.ApiKey = apiKey.Text;\n'
            '            if (UiKit.TryReadInt(concurrency.Text, out var c)) row.Concurrency = c;\n'
            '            if (UiKit.TryReadInt(priority.Text, out var p)) row.Priority = p;\n'
            '            row.Enabled = enabled.IsChecked == true;\n'
            '\n'
            '            if (existing is null) registry.AddConfig(row);')

if old_save not in text:
    raise SystemExit('save block anchor missing')
text = text.replace(old_save, new_save)

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('modal rewritten')
