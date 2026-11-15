import io

# 1) TaskGroup.Running + CloudflareSolverId (both named by the binding table)
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    public DateTime? NextReset =>'''
add1 = '''    /// <summary>How many of this group's tasks are live right now (bound as <c>Running</c>, R362).</summary>
    public int Running => Tasks.Count(t => t.IsRunning);

    /// <summary>
    /// The Cloudflare solver selected for this group, by configuration id (bound as <c>CloudflareSolverId</c>). The name
    /// stays in <c>CloudflareSolver</c>; this is the id the settings list keys on.
    /// </summary>
    public string? CloudflareSolverId { get; set; }

''' + anchor1
assert anchor1 in t1 and 'public int Running =>' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor1, add1, 1))
print('TaskGroup.Running + CloudflareSolverId')

# 2) NotificationOptions.Name — the category this options block belongs to
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Profiles.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    public string Path { get => _path; set => SetProperty(ref _path, value); }'''
add2 = anchor2 + '''

    /// <summary>
    /// Which notification category these options configure (bound as <c>Name</c>, R362) — the five the notifications page
    /// tabs between: Checkout, Decline, Captcha, Smart Actions, Other.
    /// </summary>
    public string Name { get; set; } = string.Empty;'''
assert anchor2 in t2 and 'public string Name { get; set; } = string.Empty;\n    }' not in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor2, add2, 1))
print('NotificationOptions.Name')
