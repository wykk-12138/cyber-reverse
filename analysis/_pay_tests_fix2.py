import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PaymentViewTests.cs"
t = io.open(p, encoding='utf-8').read()
# the visible-labels helper must also respect an ancestor's IsVisible: a hidden row still contributes text blocks
t = t.replace('''            .Where(t => t.IsVisible && t.Text is { Length: > 0 })''',
              '''            .Where(t => t.Text is { Length: > 0 } && IsShown(t))''')
t = t.replace('''    [Fact]
    public void MaxOpenIsHiddenWhileAutoOpenThreeDsIsOff()''',
              '''    /// <summary>True when the block and every ancestor is visible; a hidden row keeps its text blocks.</summary>
    private static bool IsShown(Control control)
    {
        for (var node = control; node is not null; node = node.Parent as Control)
            if (!node.IsVisible) return false;
        return true;
    }

    [Fact]
    public void MaxOpenIsHiddenWhileAutoOpenThreeDsIsOff()''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('helper now walks ancestors')
