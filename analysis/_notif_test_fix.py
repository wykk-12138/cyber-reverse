import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NotificationPopupTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Ui.Views.Modals;', 'using Cybersole.Ui.Views.Common;\nusing Cybersole.Ui.Views.Modals;')
t = t.replace('Common.EmptyView.Headline', 'EmptyView.Headline')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using fixed')
