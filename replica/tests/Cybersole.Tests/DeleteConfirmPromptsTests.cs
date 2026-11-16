using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for the tasks delete confirmation, the one member of the family whose body has been read.
///
/// All three texts carry the count, and the whole thing is skipped for an empty selection. The texts are the shipped
/// ones — including the parenthesised action label, which is unusual enough that a tidier rewrite would drop it.
/// </summary>
public class DeleteConfirmPromptsTests
{
    private readonly ITestOutputHelper _out;

    public DeleteConfirmPromptsTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["Tasks.DeleteConfirm.TitleFormat"] = "Delete {0} tasks?",
        ["Tasks.DeleteConfirm.MessageFormat"] =
            "Are you sure you want to delete {0} tasks?\nYou cannot undo this action.",
        ["Tasks.DeleteConfirm.ActionFormat"] = "Delete ({0}) tasks",
    };

    private static (string Title, string Message, string Action)? Tasks(int count)
        => DeleteConfirmPrompts.Tasks(count, k => Copy[k]);

    [Fact]
    public void AnEmptySelectionProducesNoConfirmation()
    {
        Assert.Null(Tasks(0));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(3)]
    [InlineData(120)]
    public void AllThreeTextsCarryTheCount(int count)
    {
        var pair = Tasks(count);
        Assert.NotNull(pair);
        _out.WriteLine(pair!.Value.Title + " | " + pair.Value.Action);

        Assert.Equal("Delete " + count + " tasks?", pair.Value.Title);
        Assert.StartsWith("Are you sure you want to delete " + count + " tasks?", pair.Value.Message,
            StringComparison.Ordinal);
        Assert.EndsWith("You cannot undo this action.", pair.Value.Message, StringComparison.Ordinal);
        Assert.Equal("Delete (" + count + ") tasks", pair.Value.Action);
    }

    [Fact]
    // The count appears in the action label inside parentheses, and only there. A rewrite that made the three
    // labels consistent would change what the button says.
    public void TheActionLabelParenthesisesTheCount()
    {
        var pair = Tasks(9);
        Assert.Equal("Delete (9) tasks", pair!.Value.Action);
        Assert.DoesNotContain("(9)", pair.Value.Title, StringComparison.Ordinal);
        Assert.DoesNotContain("(9)", pair.Value.Message, StringComparison.Ordinal);
    }

    [Fact]
    // Nothing here pluralises: the catalogue has one form per screen and passes the number through.
    public void ASingleTaskIsStillPhrasedInThePlural()
    {
        var pair = Tasks(1);
        Assert.Equal("Delete 1 tasks?", pair!.Value.Title);
        Assert.Equal("Delete (1) tasks", pair.Value.Action);
    }
}
