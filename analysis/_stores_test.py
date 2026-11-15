import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('        Assert.Equal("2 stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(2));',
'''        Assert.Equal("2 stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(2));
        Assert.Equal("No stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(0));
        Assert.Equal("1 store", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(1));''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test extended')
