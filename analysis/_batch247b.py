import io
# NotificationOptions.EnableSound -> alias of Sound (the replica named it Sound; the original binds EnableSound)
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Profiles.cs'
t = io.open(p, encoding='utf-8').read()
old = '    public bool Sound { get => _sound; set => SetProperty(ref _sound, value); }'
new = '''    public bool Sound { get => _sound; set => SetProperty(ref _sound, value); }

    /// <summary>
    /// The same switch under the original's binding name (analysis/xaml_bindings.json binds <c>EnableSound</c>).
    /// Kept as an alias rather than a second field, so there is one source of truth for "play a sound".
    /// </summary>
    public bool EnableSound { get => Sound; set => Sound = value; }'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('NotificationOptions.EnableSound alias')

# StaggerStartView.TotalTasks — the count the view spreads the starts over
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\StaggerStartView.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''    public StaggerStartView(AppServices services, IEnumerable<BotTask> tasks)
    {'''
new2 = '''    /// <summary>How many tasks are being staggered (bound as <c>TotalTasks</c>).</summary>
    public int TotalTasks => _tasks.Count;

    public StaggerStartView(AppServices services, IEnumerable<BotTask> tasks)
    {'''
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2, 1))
print('StaggerStartView.TotalTasks')
