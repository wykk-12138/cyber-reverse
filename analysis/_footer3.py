import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
# find the 'var save = SaveButton(() =>' and the first '}));' after it
start = next(i for i, l in enumerate(lines) if 'var save = SaveButton(() =>' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == '}));')
print('start', start + 1, 'end', end + 1)
new_tail = [
    '        });',
    '',
    '        BuildFooter(save);',
    '',
    '        // R340: measured on the running build — the label names the first missing input and the button only',
    '        // enables in the last state.',
    '        void Relabel()',
    '        {',
    '            save.Content = SubmitLabel(name.Text, url.Text);',
    '            save.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);',
    '        }',
    '        name.TextChanged += (_, _) => Relabel();',
    '        url.TextChanged += (_, _) => Relabel();',
    '        Relabel();',
]
lines[end:end + 1] = new_tail
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('footer closed properly')
