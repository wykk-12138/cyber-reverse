import io

# ---------------------------------------------------------------- TaskView
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding="utf-8").read()

# 1) A control cannot be re-parented. Every Refresh() rebuilt the page and re-added the same
#    ComboBox / TextBox / TextBlock, which threw "already has a visual parent".
old_build = """    private Control Build()
    {
        return new DockPanel"""
new_build = """    private Control Build()
    {
        // R73: Refresh() rebuilds the page, and these three controls are fields (their state is
        // the user's choice). A control cannot be added to a second parent, so they are detached
        // from the previous build first — without this, every refresh threw
        // "The control ComboBox already has a visual parent".
        Detach(_groups);
        Detach(_search);
        Detach(_status);

        return new DockPanel"""
if old_build not in t:
    raise SystemExit("Build anchor missing")
t = t.replace(old_build, new_build, 1)

helper = '''    /// <summary>Removes a control from whatever container the previous build put it in.</summary>
    private static void Detach(Control control)
    {
        switch (control.Parent)
        {
            case Panel panel:
                panel.Children.Remove(control);
                break;
            case ContentControl content when ReferenceEquals(content.Content, control):
                content.Content = null;
                break;
            case Decorator decorator when ReferenceEquals(decorator.Child, control):
                decorator.Child = null;
                break;
        }
    }

'''
anchor = "    private static Control Docked(Control control, Avalonia.Controls.Dock dock)"
if anchor not in t:
    raise SystemExit("Docked anchor missing")
t = t.replace(anchor, helper + anchor, 1)

# 2) Do not offer "Open In Browser" when there is no browser bridge — a status-only item is
#    exactly what DeadButtonTests exists to catch.
t = t.replace("            .WithViewer(task => Views.Common.ViewHostModal.Show(this, task.Name,\n"
              "                UiKit.Scroll(new TaskDetailsView(_services, task)), 640, 520))\n"
              "            .WithOpener(task => Status($\"No browser bridge for {task.Name} yet.\"));",
              "            .WithViewer(task => Views.Common.ViewHostModal.Show(this, task.Name,\n"
              "                UiKit.Scroll(new TaskDetailsView(_services, task)), 640, 520));\n"
              "            // Tasks.Context.OpenBrowser is deliberately not wired: there is no browser\n"
              "            // bridge to open, and a menu item that only writes a status line is a dead\n"
              "            // button. Recorded in PARITY.md instead.", 1)

# 3) Captcha Solver opens the solver window that already exists.
t = t.replace('right.Children.Add(UiKit.Button("Captcha Solver", () =>\n'
              '            Status("The captcha solver window is not wired to this page yet.")));',
              'right.Children.Add(UiKit.Button("Captcha Solver", OpenSolver));', 1)

solver = '''    /// <summary><c>Tasks.Action.CaptchaSolver</c> — the solver window that already existed.</summary>
    private void OpenSolver()
    {
        if (TopLevel.GetTopLevel(this) is not Window owner)
        {
            Status("No owner window — cannot open the solver.");
            return;
        }

        _ = new SolverWindow(_services).ShowDialog(owner);
    }

'''
t = t.replace("    private void NewGroup()", solver + "    private void NewGroup()", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("TaskView patched")

# ---------------------------------------------------------------- baseline
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
for name in ("TaskDetailsView", "TaskGroupListView"):
    line = '        "%s",\n' % name
    if line in t2:
        t2 = t2.replace(line, "", 1)
        print("removed from baseline:", name)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
