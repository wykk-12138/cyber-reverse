import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Browser\CustomBrowser.cs'
t = io.open(p, encoding='utf-8').read()

# 1) extend the actions record with a script runner (Back/Forward/Refresh are one-liners over it)
old_actions = '''public sealed record CustomBrowserActions(
    Func<string, Task> Navigate,
    Func<string, Task<string?>>? Autofill = null);'''
new_actions = '''public sealed record CustomBrowserActions(
    Func<string, Task> Navigate,
    Func<string, Task<string?>>? Autofill = null,
    Func<string, Task<string?>>? Evaluate = null);'''
assert old_actions in t
t = t.replace(old_actions, new_actions, 1)

# 2) add the seven bound members the original declares (R225)
anchor = '''    /// <summary>Opens the window against a live CDP session.</summary>'''
add = '''    /// <summary>
    /// The seven members the original binds on this window besides Navigate/Autofill — its compiled XAML lists
    /// <c>Back, Exit, Forward, Minimise, Refresh, Status, Type</c> (R225, `analysis/xaml_bindings.json`).
    /// </summary>

    /// <summary>Goes back in the bound session's history.</summary>
    public Task Back() => RunScriptAsync("history.back()");

    /// <summary>Goes forward in the bound session's history.</summary>
    public Task Forward() => RunScriptAsync("history.forward()");

    /// <summary>Reloads the bound session's page.</summary>
    public Task Refresh() => RunScriptAsync("location.reload()");

    /// <summary>Minimises the window, as the title bar's own button does.</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    /// <summary>Closes the window.</summary>
    public void Exit() => Close();

    /// <summary>
    /// Which surface this window shows. The original binds a <c>Type</c> member here; the replica has exactly one kind of
    /// surface, so it defaults to "Task" and is only a label.
    /// </summary>
    public string Type { get; set; } = "Task";

    /// <summary>The status line, which is what the original's <c>Status</c> binding shows.</summary>
    public string Status => StatusText;

    private async Task RunScriptAsync(string script)
    {
        if (_actions?.Evaluate is null)
        {
            StatusText = "No session bound.";
            return;
        }

        try
        {
            await _actions.Evaluate(script).ConfigureAwait(true);
            StatusText = script;
        }
        catch (Exception ex)
        {
            StatusText = "Script failed: " + ex.GetType().Name;
        }
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# 3) the bridge factory also supplies Evaluate
t = t.replace('''        new(new CustomBrowserActions(
            url => bridge.NavigateAsync(url),
            script => bridge.EvaluateAsync(script)), language);''',
'''        new(new CustomBrowserActions(
            url => bridge.NavigateAsync(url),
            script => bridge.EvaluateAsync(script),
            script => bridge.EvaluateAsync(script)), language);''')

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CustomBrowser: 7 bound members added')
