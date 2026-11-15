import io
pairs = [
 ("ActionsMoreFormat", "{0} ({1} more)", "SmartActions.Actions.MoreFormat"),
 ("ChangeTriggerMessage", "Changing the trigger will reset all filters and actions. Are you sure?", "SmartActions.ChangeTrigger.Message"),
 ("ChangeTriggerTitle", "Change Trigger?", "SmartActions.ChangeTrigger.Title"),
 ("PublishFormat", "Publish {0}", "SmartActions.Context.PublishFormat"),
 ("EmptyNoActionsSubtitle", "Add some smart actions to get started", "SmartActions.Empty.NoActions.Subtitle"),
 ("EmptyNoResultsSubtitle", "There are no results matching your search", "SmartActions.Empty.NoResults.Subtitle"),
 ("FiltersCountFormat", "{0} Filters", "SmartActions.Filters.CountFormat"),
 ("FiltersNone", "No Filters", "SmartActions.Filters.None"),
 ("FiltersOne", "1 Filter", "SmartActions.Filters.One"),
 ("HeaderFormat", "Smart Actions ({0})", "SmartActions.HeaderFormat"),
 ("LastRunFormat", "Triggered {0} ({1})", "SmartActions.LastRun.Format"),
 ("NewAction", "New Action", "SmartActions.NewAction"),
 ("SearchPlaceholder", "Search Smart Actions", "SmartActions.SearchPlaceholder"),
]
lines = ['', "    // ------------------------------------------------ copy from the image's locale (R413)", '    //',
         "    // The SmartActions.* strings that had no counterpart, verbatim (same table shape as the other pages).",
         "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
         '    {']
for name, value, key in pairs:
    esc = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, key))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's smart-action strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
lines.append('    /// <summary>The filters caption with the image\'s zero / one / many forms.</summary>')
lines.append('    public static string FiltersCaption(int count) => count switch')
lines.append('    {')
lines.append('        0 => FiltersNone,')
lines.append('        1 => FiltersOne,')
lines.append('        _ => string.Format(FiltersCountFormat, count),')
lines.append('    };')
lines.append('')
block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs"
t = io.open(p, encoding='utf-8').read()
brace = t.index('{', t.index('public sealed class SmartActionsView'))
line_end = t.index('\n', brace) + 1
assert 'IReadOnlyDictionary<string, string> Copy' not in t[:line_end + 4000]
t = t[:line_end] + block + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('13 smart-action strings captured')
