import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MainWindow.cs'
t = io.open(p, encoding='utf-8').read()
# CommonModals lives in Cybersole.Ui.Views, not Views.CommonModals
t = t.replace('new Views.CommonModals.NotificationView(_vm.Services).Show(this)',
              'new NotificationView(_vm.Services).Show(this)', 1)
t = t.replace('new Views.CommonModals.UserView(_vm.Services).Show(this)',
              'new UserView(_vm.Services).Show(this)', 1)
if 'using System.Globalization;' not in t:
    t = t.replace('using Avalonia;', 'using System.Globalization;\nusing Avalonia;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('namespaces fixed')
