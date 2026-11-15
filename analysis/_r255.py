import io, re

# 1) Models.Profile.Delivery
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Profiles.cs'
t = io.open(p, encoding='utf-8').read()
m = re.search(r'( *public string Name \{ get => _name; set => SetProperty\(ref _name, value\); \})', t)
assert m
add = m.group(1) + '''

    /// <summary>
    /// The delivery details this profile carries (bound as <c>Delivery</c> on Models.Profile). A profile is what the
    /// checkout form is filled from, and shipping is part of that form.
    /// </summary>
    public string Delivery { get; set; } = string.Empty;'''
t = t[:m.end()] + add + t[m.end():]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Profile.Delivery')

# 2) Settings.MonitorConcurrency
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs'
t2 = io.open(p2, encoding='utf-8').read()
m2 = re.search(r'( *public ConcurrencySettings Concurrency \{ get; set; \} = new\(\);)', t2)
assert m2
add2 = m2.group(1) + '''

    /// <summary>
    /// How many monitors run at once (bound as <c>MonitorConcurrency</c>). Distinct from <see cref="Concurrency"/>,
    /// which is the checkout pool: the settings page shows "Monitor Concurrency" as its own row.
    /// </summary>
    public int MonitorConcurrency { get; set; } = 10;'''
t2 = t2[:m2.end()] + add2 + t2[m2.end():]
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('Settings.MonitorConcurrency')

# 3) DropdownModal / InputModal: ButtonText + Placeholder
p3 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t3 = io.open(p3, encoding='utf-8').read()
for cls in ('InputModal', 'DropdownModal'):
    anchor = 'public sealed class %s : Window\n{' % cls
    assert anchor in t3, cls
    add3 = anchor + '''

    /// <summary>Label of the confirm button (bound as <c>ButtonText</c>).</summary>
    public string ButtonText { get; set; } = "OK";

    /// <summary>Watermark shown before anything is typed (bound as <c>Placeholder</c>).</summary>
    public string Placeholder { get; set; } = string.Empty;'''
    t3 = t3.replace(anchor, add3, 1)
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('InputModal + DropdownModal: ButtonText/Placeholder')
