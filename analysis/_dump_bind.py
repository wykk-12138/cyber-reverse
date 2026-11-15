import io, json
bind = json.load(io.open('xaml_bindings.json', encoding='utf-8'))
want = ['Ui.Views.Tasks.TaskView', 'Ui.Views.Proxies.ProxyView', 'Ui.Views.Accounts.AccountGrid',
        'Ui.Views.Browser.CustomBrowser', 'Ui.Views.Monitor.MonitorWindow', 'Ui.Views.MainWindow',
        'Ui.Views.Utilities.UtilitiesView']
for k in sorted(bind):
    for w in want:
        if k.endswith(w):
            print('%-46s (%d): %s' % (w, len(bind[k]), ', '.join(bind[k])))
