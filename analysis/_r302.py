import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>
    /// Removes a parameter from an action step (bound as <c>DeleteParam</c>).'''
add = '''    /// <summary>The templates this action can be built from (bound as <c>UseTemplate</c> targets).</summary>
    public IReadOnlyList<PublishedTemplate> Templates => _services.SmartActions.Templates;

    /// <summary>
    /// Loads a published template into the action being edited (bound as <c>UseTemplate</c>): its filters and its action
    /// steps replace the current ones. The name of the action is left alone, because a template is a starting point and
    /// the action still needs its own name.
    /// </summary>
    public bool UseTemplate(string title)
    {
        var template = Templates.FirstOrDefault(t => t.Title == title);
        if (template is null) return false;

        _filters.Clear();
        _filters.AddRange(template.Filters.Select(Clone));
        _action.Actions = template.Actions.Select(a => new SmartActionStep
        {
            Kind = a.Kind,
            Config = a.Config.Select(c => new SmartActionStepConfig { Name = c.Name, Required = c.Required }).ToList(),
        }).ToList();

        if (_index == 1) Navigate(1);
        if (_index == 2) Navigate(2);
        return true;
    }

    private static SmartActionFilter Clone(SmartActionFilter f) => new()
    {
        Field = f.Field,
        Operator = f.Operator,
        Value = f.Value,
        Behaviour = f.Behaviour,
        Inputs = f.Inputs.Select(i => new SmartActionFilterInput { Name = i.Name, Value = i.Value }).ToList(),
    };

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('UseTemplate + Templates added')
