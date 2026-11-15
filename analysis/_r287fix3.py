import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        // the difference is the multi-variant opening and the tax step
        Assert.Contains("FindProductMulti", multi);
        Assert.DoesNotContain("FindProductMulti", single);
        Assert.Contains("CalculateTaxes", multi);
        Assert.DoesNotContain("CalculateTaxes", single);'''
new = '''        // R287: the difference is the multi-variant opening, NOT the tax step. CalculateTaxes sits at ordinal 45 in the
        // literal at 0x034b23a5, i.e. it belongs to BOTH shapes; the earlier assertion here ("CalculateTaxes is multi
        // only") was the same defect as the single flow's missing step, restated as a guard.
        Assert.Contains("FindProductMulti", multi);
        Assert.DoesNotContain("FindProductMulti", single);
        Assert.Contains("CalculateTaxes", multi);
        Assert.Contains("CalculateTaxes", single);
        Assert.Contains("GetMerchantCode", multi);
        Assert.DoesNotContain("GetMerchantCode", single);
        Assert.Contains("EditLine", single);
        Assert.DoesNotContain("EditLine", multi);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('the distinguishing assertions now match the literal')
