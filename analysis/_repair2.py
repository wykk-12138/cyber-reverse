import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
# delete the leftover submit block (0-based 668..679 => lines 669..680) and restore BuildFooter
del_start, del_end = 668, 680
assert 'R340: the footer button names' in lines[del_start+1], lines[del_start+1]
assert 'Relabel();' in lines[del_end-1], lines[del_end-1]
del lines[del_start:del_end]
# rename the footer assignment back
for i, l in enumerate(lines):
    if l.strip() == 'var saveAction = SaveButton(() =>':
        lines[i] = l.replace('var saveAction = SaveButton(() =>', 'BuildFooter(SaveButton(() =>')
        print('footer call restored at line', i + 1)
        break
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('webhook class restored to pre-R340 shape')
