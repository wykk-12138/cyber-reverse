import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EmptyViewTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('    Assert.Contains("UiKit.Empty(EmptyView.Headline)", Ui("Settings/ProviderViews.cs"));',
              '    Assert.Contains("EmptyView.For(\\"cloudflare\\")", Ui("Settings/ProviderViews.cs"));', 1)
idx = t.rindex('}')
add = '''
    [Fact]
    public void EachPageCanCarryItsOwnSecondLine()
    {
        // R400: the Cloudflare page printed the proxies sentence; EmptyView now holds one line per page.
        Assert.Equal("Add a Cloudflare provider to get started", EmptyView.Body("cloudflare"));
        Assert.Equal("Add some proxies to get started", EmptyView.Body("proxies"));
        Assert.Equal("Add some tasks to get started", EmptyView.Body("tasks"));
        Assert.Equal(string.Empty, EmptyView.Body("no-such-page"));

        var view = EmptyView.For("cloudflare");
        _out.WriteLine(view.BodyText.Text);
        Assert.Equal("Nothing to see here", view.HeadlineText.Text);
        Assert.Equal("Add a Cloudflare provider to get started", view.BodyText.Text);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('guard updated + new test')
