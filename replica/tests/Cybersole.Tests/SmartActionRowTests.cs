using System.Collections.Generic;
using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.SmartActions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R317: the six acceptance points from <c>docs/CONTROL_DESIGN_FilterRow.md</c>, as pure logic.
///
/// <para>
/// The image binds these rows in Cybersole.Ui.Views.SmartActions: FilterRow (Filter/Inputs/IsFirst/Passed/Title/
/// ValueText), ActionRow (Action/IsFirst/Result/Tooltip), InputRow (Text/Matched) and FilterInputEntry
/// (Filter/Input/IsFirst). Passed is a value the caller supplies — judging a filter needs a CheckoutEvent and belongs to
/// the engine — so every assertion here runs without a checkout.
/// </para>
/// </summary>
public sealed class SmartActionRowTests
{
    private readonly ITestOutputHelper _out;
    public SmartActionRowTests(ITestOutputHelper output) => _out = output;

    private static SmartActionFilter Filter(string field = "Price", string op = ">", string value = "200") => new()
    {
        Field = field,
        Operator = op,
        Value = value,
        Inputs = new List<SmartActionFilterInput>
        {
            new() { Filter = field, Input = "first" },
            new() { Filter = field, Input = "second" },
        },
    };

    [Fact]
    public void TheFirstRowIsTheOnlyOneThatSaysItIsFirst()
    {
        var filters = new[] { Filter(), Filter("Size", "=", "9") };
        var rows = filters.Select((f, i) => new FilterRow(f, passed: false, isFirst: i == 0)).ToList();

        _out.WriteLine(string.Join(" | ", rows.Select(r => r.ToString())));

        Assert.True(rows[0].IsFirst);
        Assert.False(rows[1].IsFirst);
    }

    [Fact]
    public void TitleMatchesTheFilterAndAnEmptyValueReadsAsAny()
    {
        var row = new FilterRow(Filter(), passed: false, isFirst: true);
        Assert.Equal(row.Filter.ToString(), row.Title);

        var empty = new FilterRow(Filter(value: ""), passed: false, isFirst: false);
        _out.WriteLine(empty.ValueText);
        Assert.Equal("(any)", empty.ValueText);
        Assert.Equal("200", row.ValueText);
    }

    [Fact]
    public void PassedIsWhicheverTheCallerDecided()
    {
        Assert.True(new FilterRow(Filter(), passed: true, isFirst: true).Passed);
        Assert.False(new FilterRow(Filter(), passed: false, isFirst: true).Passed);
    }

    [Fact]
    public void InputsMirrorTheFilterAndOnlyTheFirstIsMarkedFirst()
    {
        var row = new FilterRow(Filter(), passed: false, isFirst: true);

        Assert.Equal(row.Filter.Inputs.Count, row.Inputs.Count);
        Assert.True(row.Inputs[0].IsFirst);
        Assert.False(row.Inputs[1].IsFirst);
        Assert.Equal("Price", row.Inputs[0].Filter);
        Assert.Equal("second", row.Inputs[1].Input);
    }

    [Fact]
    public void ActionRowsStartFirstAndCarryNoResultYet()
    {
        var step = new SmartActionStep { Name = "Notify", Kind = SmartActionKind.Webhook };
        var rows = new[] { new ActionRow(step, isFirst: true), new ActionRow(step, isFirst: false) };

        Assert.True(rows[0].IsFirst);
        Assert.False(rows[1].IsFirst);
        Assert.Equal(string.Empty, rows[0].Result);
        Assert.Equal(string.Empty, rows[0].Tooltip);
        Assert.Same(step, rows[0].Action);
    }

    [Fact]
    public void AnInputRowCarriesItsTextAndWhetherItMatched()
    {
        var hit = new InputRow("Ada", matched: true);
        var miss = new InputRow("Grace", matched: false);

        Assert.Equal("Ada", hit.Text);
        Assert.True(hit.Matched);
        Assert.False(miss.Matched);
    }

    [Fact]
    public void FilterRowAndFilterInputEntryBindableMembersAreSettable()
    {
        var initial = Filter();
        var replacement = Filter("Store", "equals", "nike");
        var row = new FilterRow(initial, passed: true, isFirst: true);
        var inputs = new[] { new FilterInputEntry("Store", "nike", isFirst: true) };

        row.Filter = replacement;
        row.Inputs = inputs;
        inputs[0].Filter = "Product";

        Assert.Same(replacement, row.Filter);
        Assert.Same(inputs, row.Inputs);
        Assert.Equal("Product", row.Inputs[0].Filter);
    }
}
