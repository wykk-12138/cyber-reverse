import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheMonitorPageCarriesTheSevenStringsAndItsSizesCaption()
    {
        // R423: Monitor.* was the last locale family with no host class. The page now exists with ONLY the wording the
        // image states — its inner layout is unverified, which the class remarks say out loud.
        var view = new Cybersole.Ui.Views.Monitor.MonitorView();
        _out.WriteLine($"{view.Entries.Count} entries");

        Assert.Equal("Monitor Feed", Cybersole.Ui.Views.Monitor.MonitorView.TabLabel);
        Assert.Equal("Search feed", Cybersole.Ui.Views.Monitor.MonitorView.SearchPlaceholder);
        Assert.Equal("Waiting for monitor entries", Cybersole.Ui.Views.Monitor.MonitorView.EmptyHeadline);
        Assert.Equal("New products and restocks will appear here", Cybersole.Ui.Views.Monitor.MonitorView.EmptySubtitle);
        Assert.Equal("No results", Cybersole.Ui.Views.Monitor.MonitorView.NoResultsTitle);

        Assert.Equal("Available sizes", Cybersole.Ui.Views.Monitor.MonitorView.SizesCaption(3));
        Assert.Equal("No available sizes", Cybersole.Ui.Views.Monitor.MonitorView.SizesCaption(0));

        view.SetEntries(new[] { "one", "two" });
        Assert.Equal(2, view.Entries.Count);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('monitor test appended')
