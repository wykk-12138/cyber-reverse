import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()

# HistoryWindow: the two window operations the binding table names
anchor = '''    public HistoryWindow(AppServices services)
    {
        Title = "Smart action history";'''
add = '''    /// <summary>Closes the history window (bound as <c>Exit</c>).</summary>
    public void Exit() => Close();

    /// <summary>Minimises the history window (bound as <c>Minimise</c>).</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    public HistoryWindow(AppServices services)
    {
        Title = "Smart action history";'''
assert anchor in t
t = t.replace(anchor, add, 1)

# SmartActionsView: OpenCreator is the "new action" path the private editor already implements
anchor2 = '''    public void ViewLogs()'''
add2 = '''    /// <summary>Opens the creator for a brand-new action (bound as <c>OpenCreator</c>).</summary>
    public void OpenCreator() => OpenActionEditor(null);

    public void ViewLogs()'''
assert anchor2 in t
t = t.replace(anchor2, add2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('HistoryWindow.Exit/Minimise + SmartActionsView.OpenCreator added')
