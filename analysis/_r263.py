import io

# 1) TaskCreatorView.Plus / Minus — the −/+ steppers observed on the original's Quantity field (R242)
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    // ── Cart ──────────────────────────────────────────────────────────────────'''
add = '''    /// <summary>
    /// Steps the "Quantity (per profile)" field up by one (bound as <c>Plus</c> on the input model). R263: the original
    /// shows −/+ steppers beside that field (measured R242); the replica had a plain number box.
    /// </summary>
    public int Plus() => StepQuantity(+1);

    /// <summary>Steps the quantity down by one, never below 1 (bound as <c>Minus</c>).</summary>
    public int Minus() => StepQuantity(-1);

    /// <summary>The quantity the field currently holds.</summary>
    public int Quantity => ReadQuantity();

    private int ReadQuantity() =>
        _quantityPerProfileBox is not null && int.TryParse(_quantityPerProfileBox.Text, out var q) ? q : 1;

    private int StepQuantity(int delta)
    {
        if (_quantityPerProfileBox is null) return 1;

        var next = Math.Max(1, ReadQuantity() + delta);
        _quantityPerProfileBox.Text = next.ToString(System.Globalization.CultureInfo.InvariantCulture);
        return next;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskCreatorView.Plus/Minus/Quantity')

# 2) SmartActionsCreator.DeleteParam
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    /// <summary>Flips a filter between "And" and "Or" (bound as <c>ToggleFilterBehaviour</c>).</summary>'''
add2 = '''    /// <summary>
    /// Removes a parameter from an action step (bound as <c>DeleteParam</c>). The parameters are
    /// <see cref="SmartActionStepConfig"/> entries — the same "Name / Required" pair the original binds as ActionConfig.
    /// </summary>
    public bool DeleteParam(int stepIndex, int paramIndex)
    {
        if (stepIndex < 0 || stepIndex >= _action.Actions.Count) return false;

        var config = _action.Actions[stepIndex].Config;
        if (paramIndex < 0 || paramIndex >= config.Count) return false;

        config.RemoveAt(paramIndex);
        if (_index == 2) Navigate(2);
        return true;
    }

    /// <summary>Adds a parameter to an action step.</summary>
    public SmartActionStepConfig? AddParam(int stepIndex, string name, bool required = false)
    {
        if (stepIndex < 0 || stepIndex >= _action.Actions.Count) return null;

        var entry = new SmartActionStepConfig { Name = name, Required = required };
        _action.Actions[stepIndex].Config.Add(entry);
        if (_index == 2) Navigate(2);
        return entry;
    }

''' + anchor2
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SmartActionsCreator.DeleteParam + AddParam')
