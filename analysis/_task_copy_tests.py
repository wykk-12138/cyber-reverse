import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheTaskDeleteConfirmationIsTheImagesWording()
    {
        Assert.Equal("Delete {0} tasks?", TaskView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} tasks?\\nYou cannot undo this action.",
            TaskView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) tasks", TaskView.DeleteConfirmActionFormat);
        Assert.Equal("Copy URL", TaskView.ContextCopyUrl);
        Assert.Equal("Move tasks to", TaskView.ContextMoveTo);
    }

    [Fact]
    public void TheTaskEmptySearchLineIsTheImagesLine()
    {
        Assert.Equal("There are no tasks matching your search", TaskView.NoResultsSubtitle);
        Assert.Equal("Multiple Products ({0})", TaskView.MultipleProductsFormat);
    }

    [Theory]
    [InlineData(1, "1 TASK SELECTED")]
    [InlineData(6, "6 TASKS SELECTED")]
    public void TheTaskSelectionCounterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(TaskView.SelectionCaption(count));
        Assert.Equal(expected, TaskView.SelectionCaption(count));
    }

    [Theory]
    [InlineData(0, "0 Selected")]
    [InlineData(3, "3 Selected")]
    public void TheGridCounterIsTheImagesWording(int count, string expected)
    {
        _out.WriteLine(TaskView.GridSelected(count));
        Assert.Equal(expected, TaskView.GridSelected(count));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('task copy tests appended')
