import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheSmartActionTableHoldsItsStringsAndForms()
    {
        // R413: SmartActions.* table plus the filters caption's zero / one / many forms.
        var copy = Cybersole.Ui.Views.SmartActions.SmartActionsView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(13, copy.Count);
        Assert.Equal("New Action", Cybersole.Ui.Views.SmartActions.SmartActionsView.Text("NewAction"));
        Assert.Equal("Smart Actions ({0})", Cybersole.Ui.Views.SmartActions.SmartActionsView.Text("HeaderFormat"));

        Assert.Equal("No Filters", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(0));
        Assert.Equal("1 Filter", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(1));
        Assert.Equal("4 Filters", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(4));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('smart-action test appended')
