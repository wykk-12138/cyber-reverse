import io

def add_member(path, anchor, member, cls=None):
    t = io.open(path, encoding='utf-8').read()
    if member.split('(')[0].split()[-1] + '(' in t and 'bound as' in t:
        pass
    assert anchor in t, anchor
    if anchor not in t:
        return False
    t = t.replace(anchor, member + anchor, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(t)
    return True

# 1) MessageBoxDialog.Type — the image's fourth field on the dialog
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
m1 = '''    /// <summary>
    /// What kind of message this is (bound as <c>Type</c>, R357). The image carries it beside the three label flags; the
    /// kinds are the ones a message box actually distinguishes here: plain information and a confirmation.
    /// </summary>
    public string Type { get; set; } = "Information";

'''
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    /// <summary>Label of the confirm button (bound as <c>ActionText</c>).</summary>'''
if 'public string Type { get; set; }' in t1:
    print('MessageBoxDialog.Type already there')
else:
    t1 = t1.replace(anchor1, m1 + anchor1, 1)
    io.open(p1, 'w', encoding='utf-8', newline='').write(t1)
    print('MessageBoxDialog.Type added')

# 2) ProfileCsvEditorView.GroupName — it already has a _group combo; expose the chosen name
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    /// <summary>The columns the editor accepts (bound as <c>ColumnChoices</c>).</summary>'''
m2 = '''    /// <summary>The group this import lands in (bound as <c>GroupName</c>).</summary>
    public string GroupName => _group.SelectedItem as string ?? string.Empty;

'''
start = t2.index('public sealed class ProfileCsvEditorView')
if 'public string GroupName =>' in t2[start:start + 1500]:
    print('ProfileCsvEditorView.GroupName already there')
else:
    t2 = t2.replace(anchor2, m2 + anchor2, 1)
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('ProfileCsvEditorView.GroupName added')
