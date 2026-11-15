import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\HomePageParityTests.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    [Fact]
    public void TheFourChartsFromTheDecompiledClassSurvive()'''
add = '''    [Fact]
    public void AnEmptyCarouselReadsZeroOfZeroAndSaysThereAreNoReleases()
    {
        // R334: measured on the running build with no data — "Releases < 0 / 0 >" and a two-line empty state.
        Assert.Equal("0 / 0", AnalyticsView.PagerCaption(1, 0));
        Assert.Equal("2 / 3", AnalyticsView.PagerCaption(2, 3));
        Assert.Equal("There are no upcoming releases", AnalyticsView.EmptyReleasesBody);
    }

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('home test added')
