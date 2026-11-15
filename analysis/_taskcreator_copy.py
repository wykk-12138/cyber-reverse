import io
pairs = [
 ("CreateTask", "Create Task", "TaskCreator.Button.CreateTask"),
 ("CreateTasksFormat", "Create {0} Tasks", "TaskCreator.Button.CreateTasksFormat"),
 ("SaveTask", "Save Task", "TaskCreator.Button.SaveTask"),
 ("SaveTasksFormat", "Save {0} Tasks", "TaskCreator.Button.SaveTasksFormat"),
 ("MonitorInput", "Monitor Input", "TaskCreator.MonitorInput"),
 ("MonitorInputDefault", "Enter input", "TaskCreator.MonitorInput.Default"),
 ("MonitorInputFormat", "Enter {0}", "TaskCreator.MonitorInput.Format"),
 ("MonitorInputMultiple", "Multiple inputs", "TaskCreator.MonitorInput.Multiple"),
 ("MultiCart", "Multi Cart active", "TaskCreator.MultiCart"),
 ("ProfileMultiple", "Multiple profiles", "TaskCreator.Profile.Multiple"),
 ("ProfileSelect", "Select profile", "TaskCreator.Profile.Select"),
 ("ProxiesMultiple", "Multiple proxy groups", "TaskCreator.Proxies.Multiple"),
 ("ProxiesSelect", "Select proxy group", "TaskCreator.Proxies.Select"),
 ("SizeMultiple", "Multiple sizes", "TaskCreator.Size.Multiple"),
 ("SizeSelect", "Select sizes", "TaskCreator.Size.Select"),
 ("StartTimeMultiple", "Multiple start times", "TaskCreator.StartTime.Multiple"),
 ("StartTimeSet", "Set start time", "TaskCreator.StartTime.Set"),
 ("StoreMultiple", "Multiple stores", "TaskCreator.Store.Multiple"),
 ("StoreSelect", "Select store", "TaskCreator.Store.Select"),
]
lines = ['', "    // ------------------------------------------------ copy from the image's locale (R412)", '    //',
         "    // The TaskCreator.* strings that had no counterpart, verbatim. Same table shape as the other two pages.",
         "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
         '    {']
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's task-creator strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public void Close()'''
i = t.index('public sealed class TaskCreatorView')
seg = t[i:i+3000]
assert 'IReadOnlyDictionary<string, string> Copy' not in seg
# insert right after the class opening brace
brace = t.index('{', t.index('public sealed class TaskCreatorView'))
line_end = t.index('\n', brace) + 1
t = t[:line_end] + block + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('19 TaskCreator strings captured')
