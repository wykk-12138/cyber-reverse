import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccountStoreListTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('Cybersole.Ui.Views.Accounts.AccountModals.Platforms', 'StoreCatalog.Platforms')
t = t.replace('AccountModalsPlatforms', 'Platforms')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using StoreCatalog.Platforms')
