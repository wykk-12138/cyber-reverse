import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheAnalyticsTablesHoldTheirStrings()
    {
        // R415: Checkout.* and Release.* — the five words the analytics pages were missing.
        var copy = Cybersole.Ui.Views.Analytics.CheckoutView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(5, copy.Count);
        Assert.Equal("Order {0}", Cybersole.Ui.Views.Analytics.CheckoutView.Text("OrderFormat"));
        Assert.Equal("Out for delivery", Cybersole.Ui.Views.Analytics.CheckoutView.Text("OutForDelivery"));
        Assert.Equal("Scheduled Delivery", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ScheduledDelivery"));
        Assert.Equal("Add Tasks", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ReleaseAddTasks"));
        Assert.Equal("Check back later", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ReleaseEmptyCheckBack"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('analytics copy test appended')
