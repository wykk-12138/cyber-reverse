import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\RailWidthTests.cs'
t = io.open(p, encoding='utf-8').read()
add = '''
    [Fact]
    public void TheBillingColumnsAreTheMeasuredRatios()
    {
        // R223: Profile 1.00 / Email 1.28 / Card Holder 1.29 / Card 1.00 / Shipping 1.00 (last column = remainder)
        var billing = View("BillingView.cs");
        Assert.Contains("\\"18,1.0*,1.28*,1.29*,1.0*,1.0*\\"", billing);
        Assert.Contains("measured column proportions, not equal stars", billing);
        Assert.Contains("absorbs the remainder", billing);
    }
}
'''
t = t.rstrip()
assert t.endswith('}')
t = t[:t.rfind('}')] + add
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test appended')
