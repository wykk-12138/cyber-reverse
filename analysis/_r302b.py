import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()

start = t.index('    /// <summary>The templates this action can be built from (bound as <c>UseTemplate</c> targets).</summary>')
end = t.index('    /// <summary>\n    /// Removes a parameter from an action step (bound as <c>DeleteParam</c>).')
new = '''    /// <summary>The templates a new action can be built from (bound as <c>UseTemplate</c> targets).</summary>
    public IReadOnlyList<PublishedTemplate> Templates => _services.Config.SmartActions.Templates;

    /// <summary>
    /// Builds this action from a published template (bound as <c>UseTemplate</c>).
    ///
    /// <para>
    /// A template carries only metadata — a title, a description, a group and the id of the action it was published from
    /// (<see cref="PublishedTemplate.SourceActionId"/>) — so using one means copying that source action's filters and
    /// steps. The name of the action being edited is left alone: a template is a starting point.
    /// </para>
    /// </summary>
    public bool UseTemplate(string title)
    {
        var template = Templates.FirstOrDefault(t => t.Title == title);
        if (template is null || string.IsNullOrEmpty(template.SourceActionId)) return false;

        var source = _services.Config.SmartActions.Actions.FirstOrDefault(a => a.Id == template.SourceActionId);
        if (source is null) return false;

        _filters.Clear();
        foreach (var filter in source.Filters)
            _filters.Add(new SmartActionFilter
            {
                Field = filter.Field,
                Operator = filter.Operator,
                Value = filter.Value,
                Behaviour = filter.Behaviour,
                Inputs = filter.Inputs.Select(i => new SmartActionFilterInput { Filter = i.Filter, Input = i.Input }).ToList(),
            });

        _action.Actions = source.Actions.Select(a => new SmartActionStep
        {
            Name = a.Name,
            Kind = a.Kind,
            Target = a.Target,
            Config = a.Config.Select(cfg => new SmartActionStepConfig { Name = cfg.Name, Required = cfg.Required }).ToList(),
        }).ToList();

        if (_index == 1) Navigate(1);
        if (_index == 2) Navigate(2);
        return true;
    }

'''
t = t[:start] + new + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('UseTemplate rewritten against the real model shapes')
