import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\HomePageParityTests.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    [Fact]
    public void AnEmptyCarouselReadsZeroOfZeroAndSaysThereAreNoReleases()'''
add = '''    [Fact]
    public void TheSpendSegmentSaysMoneySpentAndPrintsADollarFigure()
    {
        // R335: measured on the running build — the caption is "Money Spent" (capital S) and the figure is "$0".
        Assert.Equal("Checkouts", AnalyticsView.SegmentCaption(0));
        Assert.Equal("Money Spent", AnalyticsView.SegmentCaption(1));
        Assert.Equal("$0", AnalyticsView.SpendFigure(0m));
    }

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('spend test added')
