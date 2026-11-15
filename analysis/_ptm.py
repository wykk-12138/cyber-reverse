import io
# 1) PublishTemplateModal.Groups — the list the dialog shows
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    public PublishTemplateModal(AppServices services, SmartAction? action = null)'''
add1 = '''    /// <summary>The task groups a template can be published to (bound as <c>Groups</c>). One entry when there are none.</summary>
    public IReadOnlyList<string> Groups => _groups.ItemsSource?.Cast<string>().ToList() ?? new List<string>();

''' + anchor1
assert anchor1 in t1 and 'public IReadOnlyList<string> Groups =>' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor1, add1, 1))
print('PublishTemplateModal.Groups added')

# 2) GroupGrid.Items / Store — the grid keeps a list and the store it is filtered to
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\GroupGrid.cs"
import os
if not os.path.exists(p2):
    p2 = [l.split('|')[0] for l in os.popen('findstr /S /M /C:"class GroupGrid" src\\Cybersole.Ui\\*.cs').read().split()]
    print('candidates:', p2)
