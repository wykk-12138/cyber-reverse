import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>The templates a new action can be built from (bound as <c>UseTemplate</c> targets).</summary>'''
add = '''    /// <summary>
    /// The filters as rows the editor can render (R317). IsFirst is decided by position — the member's plainest reading —
    /// and Passed is left false here: judging needs a CheckoutEvent, which belongs to the engine (see FilterRow).
    /// </summary>
    public IReadOnlyList<FilterRow> FilterRows =>
        _filters.Select((f, index) => new FilterRow(f, passed: false, isFirst: index == 0)).ToList();

    /// <summary>The steps as rows the editor can render; Result and Tooltip stay empty until a step has run.</summary>
    public IReadOnlyList<ActionRow> ActionRows =>
        _action.Actions.Select((a, index) => new ActionRow(a, index == 0)).ToList();

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('FilterRows / ActionRows wired')
