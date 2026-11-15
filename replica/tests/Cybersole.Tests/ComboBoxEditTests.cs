using System.Linq;
using Cybersole.Ui.Views.Controls;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R312: the five acceptance points written in <c>docs/CONTROL_DESIGN_ComboBoxEdit.md</c>.
///
/// <para>
/// The image binds RemoveTokenCommand / ClearSelectionCommand on Cybersole.Ui.Controls.ComboBoxEdit, so the two things a
/// rebinding addresses are these methods; the rest of the class exists to make them meaningful (tokens, group headings,
/// an add path that refuses duplicates).
/// </para>
/// </summary>
public sealed class ComboBoxEditTests
{
    private readonly ITestOutputHelper _out;
    public ComboBoxEditTests(ITestOutputHelper output) => _out = output;

    private static ComboBoxEdit Build(params string[] texts)
    {
        var combo = new ComboBoxEdit();
        combo.SetOptions(texts.Select(t => new ComboBoxEdit.Option(t)));
        return combo;
    }

    [Fact]
    public void RemoveTokenDropsItAndRaisesChangedOnce()
    {
        var combo = Build("a", "b");
        combo.Add("a");
        combo.Add("b");

        var raised = 0;
        combo.Changed += (_, _) => raised++;

        Assert.True(combo.RemoveToken("a"));
        _out.WriteLine("selected after remove: " + string.Join(",", combo.Selected));

        Assert.Equal(new[] { "b" }, combo.Selected);
        Assert.Equal(1, raised);
    }

    [Fact]
    public void ClearSelectionEmptiesItAndReportsTheCount()
    {
        var combo = Build("a", "b", "c");
        foreach (var t in new[] { "a", "b", "c" }) combo.Add(t);

        Assert.Equal(3, combo.ClearSelection());
        Assert.Empty(combo.Selected);
        Assert.Equal(0, combo.ClearSelection());   // idempotent, and reports nothing removed
    }

    [Fact]
    public void GroupHeadingsFollowTheOptionOrder()
    {
        var combo = new ComboBoxEdit();
        combo.SetOptions(new[]
        {
            new ComboBoxEdit.Option("one", "First"),
            new ComboBoxEdit.Option("two", "First"),
            new ComboBoxEdit.Option("three", "Second"),
        });

        var rows = combo.Rows.ToList();
        _out.WriteLine(string.Join(" | ", rows.Select(r => r.ToString())));

        Assert.Equal(5, rows.Count);   // two headings + three options
        Assert.Equal("First", ((ComboBoxEdit.ComboBoxGroupHeader)rows[0]).Name);
        Assert.Equal("one", ((ComboBoxEdit.Option)rows[1]).Text);
        Assert.Equal("two", ((ComboBoxEdit.Option)rows[2]).Text);
        Assert.Equal("Second", ((ComboBoxEdit.ComboBoxGroupHeader)rows[3]).Name);
    }

    [Fact]
    public void NoOptionsMeansAnEmptyDropdownAndNoCrash()
    {
        var combo = new ComboBoxEdit();
        combo.SetOptions(System.Array.Empty<ComboBoxEdit.Option>());

        Assert.Empty(combo.Options);
        Assert.Empty(combo.Rows);
        Assert.Equal(0, combo.ClearSelection());
        Assert.False(combo.RemoveToken("nothing"));
    }

    [Fact]
    public void DuplicateTextsOnlyLoseTheFirstToken()
    {
        var combo = new ComboBoxEdit();          // no options: Add accepts anything, which is how a free-text caller uses it
        combo.Add("x");
        combo.Add("x");

        Assert.Single(combo.Selected);           // Add refuses a duplicate
        Assert.True(combo.RemoveToken("x"));
        Assert.Empty(combo.Selected);
        Assert.False(combo.RemoveToken("x"));
    }
}
