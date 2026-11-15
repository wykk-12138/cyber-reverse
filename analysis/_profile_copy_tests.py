import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheProfileContextMenuIsTheImagesWording()
    {
        Assert.Equal("Clone Profiles", ProfileView.ContextClone);
        Assert.Equal("Create Test Profile", ProfileView.ContextCreateTest);
        Assert.Equal("Open in CSV Editor", ProfileView.ContextCsvEditor);
        Assert.Equal("Delete Profiles", ProfileView.ContextDelete);
        Assert.Equal("Edit Profiles", ProfileView.ContextEdit);
    }

    [Fact]
    public void TheProfileDeleteConfirmationIsTheImagesWording()
    {
        Assert.Equal("Delete {0} profiles?", ProfileView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} profiles?\\nYou cannot undo this action.",
            ProfileView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) profiles", ProfileView.DeleteConfirmActionFormat);
        Assert.Equal("There are no profiles matching your search", ProfileView.NoResultsSubtitle);
    }

    [Theory]
    [InlineData(0, "0 Profiles Loaded")]
    [InlineData(1, "1 Profile Loaded")]
    [InlineData(4, "4 Profiles Loaded")]
    public void TheProfileFooterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(ProfileView.Loaded(count));
        Assert.Equal(expected, ProfileView.Loaded(count));
    }

    [Theory]
    [InlineData(1, "1 PROFILE SELECTED")]
    [InlineData(2, "2 PROFILES SELECTED")]
    public void TheProfileSelectionCounterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(ProfileView.SelectionCaption(count));
        Assert.Equal(expected, ProfileView.SelectionCaption(count));
    }
'''
t = t[:idx] + add + '}\n'
t = t.replace('using Cybersole.Ui.Views.Proxies;', 'using Cybersole.Ui.Views.Profiles;\nusing Cybersole.Ui.Views.Proxies;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('profile copy tests appended')
