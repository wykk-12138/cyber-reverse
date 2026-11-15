import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

close_impl = '''    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool Close()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

'''

# TaskDetailsView: has `public bool Close()` already in the backup? check
if 'public sealed class TaskDetailsView' in t:
    seg_start = t.index('public sealed class TaskDetailsView')
    seg = t[seg_start:seg_start + 1200]
    if 'public bool Close()' not in seg:
        anchor = '    public TaskDetailsView(AppServices services, BotTask task)'
        assert anchor in t
        t = t.replace(anchor, close_impl + anchor, 1)
        print('TaskDetailsView.Close added')

# TaskCreatorView: close its host
seg_start = t.index('public sealed class TaskCreatorView')
seg = t[seg_start:t.index('public sealed class TaskGroupView')]
if 'public bool Close()' not in seg:
    anchor2 = '    private Control BuildSetup(BotTask? existing)'
    assert anchor2 in t
    t = t.replace(anchor2, close_impl + anchor2, 1)
    print('TaskCreatorView.Close added')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
