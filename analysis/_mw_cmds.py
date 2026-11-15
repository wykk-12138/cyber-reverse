import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\MainWindow.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    private int TabIndex => Math.Max(0, _tabs.SelectedIndex);'''
add = '''    private int TabIndex => Math.Max(0, _tabs.SelectedIndex);

    // ------------------------------------------------ bound commands (R232)
    //
    // The original binds these on MainWindow (analysis/xaml_bindings.json):
    //   Clock, Exit, Minimise, Navigate, OpenMonitor, OpenNotifications, OpenProfile
    // plus one property per view. Several were reachable only as inline toolbar lambdas; the rest were missing.

    /// <summary>Opens the monitor window (bound as <c>OpenMonitor</c>).</summary>
    public void OpenMonitor() => new MonitorWindow(_vm.Services).Show(this);

    /// <summary>Opens the notification centre (bound as <c>OpenNotifications</c>).</summary>
    public void OpenNotifications() => new Views.CommonModals.NotificationView(_vm.Services).Show(this);

    /// <summary>Opens the account/profile window (bound as <c>OpenProfile</c>).</summary>
    public void OpenProfile() => new Views.CommonModals.UserView(_vm.Services).Show(this);

    /// <summary>
    /// Switches to a tab by name — the same six names the tabs carry (bound as <c>Navigate</c>). Returns false for a
    /// name it does not know, so a caller can tell "switched" from "no such tab".
    /// </summary>
    public bool Navigate(string? tab)
    {
        if (string.IsNullOrWhiteSpace(tab)) return false;

        for (var i = 0; i < _tabs.ItemCount; i++)
        {
            if (_tabs.Items[i] is not TabItem item) continue;
            if (!string.Equals(item.Header as string, tab, StringComparison.OrdinalIgnoreCase)) continue;

            _tabs.SelectedIndex = i;
            return true;
        }

        return false;
    }

    /// <summary>Minimises the shell (bound as <c>Minimise</c>).</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    /// <summary>Closes the shell (bound as <c>Exit</c>).</summary>
    public void Exit() => Close();

    /// <summary>The local time as the title bar shows it (bound as <c>Clock</c>).</summary>
    public string Clock => DateTime.Now.ToString("HH:mm:ss", CultureInfo.InvariantCulture);'''
assert anchor in t
t = t.replace(anchor, add, 1)

# the toolbar's Monitor button now goes through the command
t = t.replace('Btn("Monitor", () => new MonitorWindow(_vm.Services).Show(this)),', 'Btn("Monitor", OpenMonitor),', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('MainWindow bound commands added')
