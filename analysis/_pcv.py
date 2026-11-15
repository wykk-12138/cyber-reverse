import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>False once the profile exists 鈥?the creator is "creating" until it is saved (bound as <c>IsCreating</c>).</summary>
    public bool IsCreating => !_saved;'''
if anchor not in t:
    anchor = '''    public bool IsCreating => !_saved;'''
add = '''    /// <summary>
    /// Which step the wizard shows (bound as <c>Navigate</c>, get and set in the image). The steps are the tabs the creator
    /// builds — "Details", "Payment", "Advanced" — and setting this selects one, ignoring a name that is not a step.
    /// </summary>
    public string Navigate
    {
        get => _step;
        set
        {
            if (string.IsNullOrWhiteSpace(value)) return;
            _step = value;
            if (_tabs is not null)
            {
                foreach (var item in _tabs.Items.OfType<TabItem>())
                {
                    if (string.Equals(item.Header as string, value, StringComparison.OrdinalIgnoreCase))
                    {
                        _tabs.SelectedItem = item;
                        break;
                    }
                }
            }
        }
    }

    /// <summary>How many profiles the wizard will create — one unless it is in bulk mode (bound as <c>Count</c>).</summary>
    public int Count => IsBulk ? Names.Count : 1;

    /// <summary>The profile being edited (bound as <c>Profile</c>).</summary>
    public Profile Profile => _profile;

    /// <summary>The names the wizard will use, one per profile (bound as <c>Names</c>, read-only).</summary>
    public IReadOnlyList<string> Names => new[] { _profile.Name };

    /// <summary>The payment step (bound as <c>PaymentView</c>): true once the wizard has built its tabs.</summary>
    public bool PaymentView => _tabs is not null;

    /// <summary>The advanced step (bound as <c>AdvancedView</c>): same condition as <see cref="PaymentView"/>.</summary>
    public bool AdvancedView => _tabs is not null;

    private string _step = "Details";
    private TabControl? _tabs;

''' + anchor
assert anchor in t and 'public string Navigate' not in t
t = t.replace(anchor, add, 1)
# remember the tab control so Navigate can select
t = t.replace('        var tabs = new TabControl { Height = 470 };', '        var tabs = new TabControl { Height = 470 };\n        _tabs = tabs;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProfileCreatorView gains Navigate/Count/Profile/Names/PaymentView/AdvancedView')
