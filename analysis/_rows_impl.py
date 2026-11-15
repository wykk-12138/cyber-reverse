import io, os
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionRows.cs"
code = '''using System.Collections.Generic;
using System.Linq;
using Cybersole.Core.Models;

namespace Cybersole.Ui.Views.SmartActions;

/// <summary>
/// One filter in the smart-action editor (Cybersole.Ui.Views.SmartActions.FilterRow, R317).
///
/// <para>
/// The image binds Filter, Inputs, IsFirst, Passed, Title and ValueText here. <b>Passed is passed in</b> rather than
/// evaluated in the row: judging a filter needs a CheckoutEvent and belongs to the engine, so the row stays a pure view
/// of one decision and can be tested without running a checkout.
/// </para>
/// </summary>
public sealed class FilterRow
{
    public FilterRow(SmartActionFilter filter, bool passed, bool isFirst)
    {
        Filter = filter;
        Passed = passed;
        IsFirst = isFirst;
        Title = filter.ToString();
        ValueText = string.IsNullOrWhiteSpace(filter.Value) ? "(any)" : filter.Value;

        Inputs = filter.Inputs
            .Select((input, index) => new FilterInputEntry(filter.Field, input.Input, index == 0))
            .ToList();
    }

    /// <summary>The filter itself (bound as <c>Filter</c>).</summary>
    public SmartActionFilter Filter { get; }

    /// <summary>The filter's inputs, each knowing whether it is the first (bound as <c>Inputs</c>).</summary>
    public IReadOnlyList<FilterInputEntry> Inputs { get; }

    /// <summary>True for the first row in the list (bound as <c>IsFirst</c>).</summary>
    public bool IsFirst { get; }

    /// <summary>Whether this filter passed, as decided by the caller (bound as <c>Passed</c>).</summary>
    public bool Passed { get; }

    /// <summary>"Field Operator Value" (bound as <c>Title</c>).</summary>
    public string Title { get; }

    /// <summary>The value as shown, with "(any)" for an empty one (bound as <c>ValueText</c>).</summary>
    public string ValueText { get; }

    public override string ToString() => Title + " -> " + ValueText;
}

/// <summary>One input of a filter, in the row that shows it (bound as <c>FilterInputEntry</c>).</summary>
public sealed class FilterInputEntry
{
    public FilterInputEntry(string filter, string input, bool isFirst)
    {
        Filter = filter;
        Input = input;
        IsFirst = isFirst;
    }

    /// <summary>The filter this input belongs to (bound as <c>Filter</c>).</summary>
    public string Filter { get; }

    /// <summary>The input's current value (bound as <c>Input</c>).</summary>
    public string Input { get; }

    /// <summary>True for the first input of its filter (bound as <c>IsFirst</c>).</summary>
    public bool IsFirst { get; }
}

/// <summary>One step in the smart-action editor (bound as <c>ActionRow</c>).</summary>
public sealed class ActionRow
{
    public ActionRow(SmartActionStep action, bool isFirst, string result = "", string tooltip = "")
    {
        Action = action;
        IsFirst = isFirst;
        Result = result;
        Tooltip = tooltip;
    }

    /// <summary>The step itself (bound as <c>Action</c>).</summary>
    public SmartActionStep Action { get; }

    /// <summary>True for the first row in the list (bound as <c>IsFirst</c>).</summary>
    public bool IsFirst { get; }

    /// <summary>The last result for this step, empty until it has run (bound as <c>Result</c>).</summary>
    public string Result { get; }

    /// <summary>The explanation shown beside the result (bound as <c>Tooltip</c>).</summary>
    public string Tooltip { get; }
}

/// <summary>One line of a suggestion list (bound as <c>InputRow</c>). No page uses it yet — see R265's rule.</summary>
public sealed class InputRow
{
    public InputRow(string text, bool matched)
    {
        Text = text;
        Matched = matched;
    }

    /// <summary>The text shown (bound as <c>Text</c>).</summary>
    public string Text { get; }

    /// <summary>Whether this line matches what the user typed (bound as <c>Matched</c>).</summary>
    public bool Matched { get; }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('four row types written')
