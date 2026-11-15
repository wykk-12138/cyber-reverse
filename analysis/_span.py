import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()
a = t.index('/// <summary>Cybersole.Ui.Views.Settings.Modals.WebhookCreatorView')
b = t.index('/// <summary>\n/// Cybersole.Ui.Views.Settings.Modals.ShippingRatesCreatorView')
old = t[a:b]
print('replacing', len(old), 'chars')
print('--- tail of the old span ---')
print(old[-700:])
