import io
R = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests'

for name, page, headline, body in (
    ('TasksPageTests.cs', 'tasks', 'Nothing to see here', 'Add some tasks to get started'),
    ('ProxiesPageTests.cs', 'proxies', 'Nothing to see here', 'Add some proxies to get started'),
):
    p = R + '\\' + name
    t = io.open(p, encoding='utf-8').read()
    old = '''        var grid = new %s(new List<%s>());
        var root = (DockPanel)grid.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var panel = body.Children.OfType<StackPanel>().Single();
        var texts = panel.Children.OfType<TextBlock>().Select(t => t.Text).ToList();

        _out.WriteLine(string.Join(" / ", texts));
        Assert.Equal(new[] { "%s", "%s" }, texts);'''

    cls = 'TaskGrid' if page == 'tasks' else 'ProxyGrid'
    item = 'BotTask' if page == 'tasks' else 'Proxy'
    old_c = old % (cls, item, headline, body)

    new_c = '''        var grid = new %s(new List<%s>());
        var root = (DockPanel)grid.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;

        // R209: the empty state is the shared EmptyView now — glyph, headline, one page-specific line — which is what
        // the running build draws. This used to assert a bare two-TextBlock StackPanel because that is all the replica
        // had.
        var empty = body.Children.OfType<Cybersole.Ui.Views.Common.EmptyView>().Single();
        _out.WriteLine(empty.HeadlineText.Text + " / " + empty.BodyText.Text);

        Assert.Equal("%s", empty.HeadlineText.Text);
        Assert.Equal("%s", empty.BodyText.Text);
        Assert.NotNull(empty.Icon);'''

    new_c = new_c % (cls, item, headline, body)
    assert old_c in t, name
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old_c, new_c))
    print('updated', name)
