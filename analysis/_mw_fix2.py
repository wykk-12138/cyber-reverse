import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MainWindow.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('new NotificationView(_vm.Services).Show(this)', 'new Modals.NotificationView(_vm.Services).Show(this)', 1)
t = t.replace('new UserView(_vm.Services).Show(this)', 'new Modals.UserView(_vm.Services).Show(this)', 1)
if 'using Cybersole.Ui.Views.Modals;' not in t:
    t = t.replace('using Cybersole.Ui.Views.Accounts;', 'using Cybersole.Ui.Views.Accounts;\nusing Cybersole.Ui.Views.Modals;', 1)
    t = t.replace('new Modals.NotificationView', 'new NotificationView').replace('new Modals.UserView', 'new UserView')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using added')
