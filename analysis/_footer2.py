import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

# 1) drop the extra submit button block; keep a single SaveButton we can relabel
bad = '''        // R340: the footer button names the first missing input and only lights up in the last state, as measured.
        var submit = UiKit.Button(SubmitLabel(name.Text, url.Text), () => { });
        submit.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        void Relabel()
        {
            submit.Content = SubmitLabel(name.Text, url.Text);
            submit.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        }
        name.TextChanged += (_, _) => Relabel();
        url.TextChanged += (_, _) => Relabel();
        Relabel();

        var saveAction = SaveButton(() =>'''
good = '''        // R340: the footer button names the first missing input and only lights up in the last state, as measured.
        var save = SaveButton(() =>'''
assert bad in t
t = t.replace(bad, good, 1)

# 2) close the SaveButton assignment, add BuildFooter(save) and the relabel wiring after it
marker = '''        }));

'''
i = t.index('var save = SaveButton(() =>', t.index('public sealed class WebhookCreatorView'))
j = t.index(marker, i) + len(marker)
tail = '''        });

        BuildFooter(save);

        void Relabel()
        {
            save.Content = SubmitLabel(name.Text, url.Text);
            save.IsEnabled = IsWebhookUrl(url.Text) && !string.IsNullOrWhiteSpace(name.Text);
        }
        name.TextChanged += (_, _) => Relabel();
        url.TextChanged += (_, _) => Relabel();
        Relabel();
'''
t = t[:i] + t[i:j - len(marker)] + tail + t[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('footer restructured around one SaveButton')
