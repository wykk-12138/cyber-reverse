import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding='utf-8').read()

old_row = '''                // R77 caveat: the live page at rest shows only "Auto Open 3DS" \u2014 this second row
                // is not on it. Either it appears only when Auto Open 3DS is Yes, or the label is
                // an orphan. The combo could not be driven to find out (see PaymentView.LiveControls
                // and docs/SESSION_STATE.md), so the row stays: the property is real, MainWindow
                // reads it, and hiding it would strand the value with no editor.
                UiKit.Row("Max Open", auto3dsLimit)),'''
new_row = '''                // R330 settled the R77 caveat on the running build: with "Auto Open 3DS" on Yes a
                // "Max Open" row appears under it (value 5); switching back to No removes it again.
                // So the row is conditional, not missing \u2014 maxOpen is built below and toggled with the combo.
                maxOpen),'''
assert old_row in t
t = t.replace(old_row, new_row, 1)

# build maxOpen after auto3dsLimit and wire the toggle
old_build = '''        var auto3ds = UiKit.Combo(new[] { "No", "Yes" }, s.AutoOpen3DS ? 1 : 0);
        var auto3dsLimit = UiKit.Number(s.AutoOpen3DSLimit);'''
new_build = '''        var auto3ds = UiKit.Combo(new[] { "No", "Yes" }, s.AutoOpen3DS ? 1 : 0);
        var auto3dsLimit = UiKit.Number(s.AutoOpen3DSLimit);

        // R330: measured on the running build \u2014 "Max Open" only exists while "Auto Open 3DS" is Yes.
        var maxOpen = UiKit.Row("Max Open", auto3dsLimit);
        maxOpen.IsVisible = s.AutoOpen3DS;
        auto3ds.SelectionChanged += (_, _) => maxOpen.IsVisible = auto3ds.SelectedIndex == 1;'''
assert old_build in t
t = t.replace(old_build, new_build, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Max Open row is now conditional (R330)')
