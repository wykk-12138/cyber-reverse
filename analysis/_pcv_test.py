import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CloseAndOpenFamilyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheProfileCreatorReportsItsStepAndCount()
    {
        // R419: ProfileCreatorView binds Navigate / Count / Profile / Names / PaymentView / AdvancedView.
        using var services = TestServices.Create();
        var creator = new Cybersole.Ui.Views.Profiles.ProfileCreatorView(services);

        _out.WriteLine($"{creator.Navigate} / {creator.Count} / {creator.Names.Count} / {creator.PaymentView}");
        Assert.Equal("Details", creator.Navigate);
        Assert.Equal(1, creator.Count);
        Assert.Single(creator.Names);
        Assert.True(creator.PaymentView);
        Assert.True(creator.AdvancedView);
        Assert.NotNull(creator.Profile);

        creator.IsBulk = true;
        Assert.Equal(1, creator.Count);   // bulk with one name is still one profile
        creator.Navigate = "Payment";
        Assert.Equal("Payment", creator.Navigate);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test appended')
