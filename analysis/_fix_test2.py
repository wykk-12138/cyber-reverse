import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GeneralSettingsLayoutTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        // the measured order: Default Delays, then Quicktask, then Shopify
        var delays = source.IndexOf("\\"Default Delays\\"", System.StringComparison.Ordinal);
        var quick = source.IndexOf("\\"Quicktask Settings\\"", System.StringComparison.Ordinal);
        var shopify = source.IndexOf("\\"Shopify Settings\\"", System.StringComparison.Ordinal);'''
new = '''        // the measured order: Default Delays, then Quicktask, then Shopify. Search for the TextBlock forms, not the
        // bare strings — the explanatory comment above the controls also names the section, and a bare search matches
        // it first (measured: quick@10064 < delays@10167).
        var delays = source.IndexOf("Text = \\"Default Delays\\"", System.StringComparison.Ordinal);
        var quick = source.IndexOf("Text = \\"Quicktask Settings\\"", System.StringComparison.Ordinal);
        var shopify = source.IndexOf("Text = \\"Shopify Settings\\"", System.StringComparison.Ordinal);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('patched order assertion')
