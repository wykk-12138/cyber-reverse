import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''                    Text = "Nothing to see here",
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = FontWeight.SemiBold,''',
'''                    Text = EmptyView.Headline,
                    HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                    FontWeight = FontWeight.SemiBold,''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('store presets block folded')
