import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Adds a filter and repaints step 2 (bound as <c>AddFilter</c>).</summary>'''
add = '''    /// <summary>Adds an action step to the rule (bound as <c>AddAction</c>).</summary>
    public SmartActionStep AddAction(SmartActionKind kind = SmartActionKind.Notification, string? name = null)
    {
        var step = new SmartActionStep
        {
            Name = string.IsNullOrWhiteSpace(name) ? "Action " + (_action.Actions.Count + 1) : name!.Trim(),
            Kind = kind,
            Target = _action.Target,
        };
        _action.Actions.Add(step);
        if (_index != 2) Navigate(2); else Navigate(2);
        return step;
    }

    /// <summary>Removes the action at <paramref name="index"/> (bound as <c>DeleteAction</c>).</summary>
    public bool DeleteAction(int index)
    {
        if (index < 0 || index >= _action.Actions.Count) return false;
        _action.Actions.RemoveAt(index);
        if (_index == 2) Navigate(2);
        return true;
    }

    /// <summary>Adds an input to the filter at <paramref name="filterIndex"/> (bound as <c>AddInput</c>).</summary>
    public SmartActionFilterInput? AddInput(int filterIndex, string filterName, string input)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return null;

        var entry = new SmartActionFilterInput { Filter = filterName, Input = input };
        _filters[filterIndex].Inputs.Add(entry);
        if (_index == 1) Navigate(1);
        return entry;
    }

    /// <summary>Removes an input from a filter (bound as <c>DeleteInput</c>).</summary>
    public bool DeleteInput(int filterIndex, int inputIndex)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return false;
        var inputs = _filters[filterIndex].Inputs;
        if (inputIndex < 0 || inputIndex >= inputs.Count) return false;
        inputs.RemoveAt(inputIndex);
        if (_index == 1) Navigate(1);
        return true;
    }

    /// <summary>Flips a filter between "And" and "Or" (bound as <c>ToggleFilterBehaviour</c>).</summary>
    public string? ToggleFilterBehaviour(int filterIndex)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return null;

        var filter = _filters[filterIndex];
        filter.Behaviour = string.Equals(filter.Behaviour, "Or", StringComparison.OrdinalIgnoreCase) ? "And" : "Or";
        if (_index == 1) Navigate(1);
        return filter.Behaviour;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('five creator commands added')
