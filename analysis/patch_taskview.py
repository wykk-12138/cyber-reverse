import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding="utf-8").read()

subs = [
    # No static Show helpers on those views; host them the way every other modal is hosted.
    ('.WithViewer(task => _ = TaskDetailsView.ShowOrNull(this, _services, task))',
     '.WithViewer(task => Views.Common.ViewHostModal.Show(this, task.Name,\n'
     '                UiKit.Scroll(new TaskDetailsView(_services, task)), 640, 520))'),
    ('Menu("Group Settings", () => TaskGroupListView.ShowOrNull(this, _services)),',
     'Menu("Group Settings", () => Views.Common.ViewHostModal.Show(this, "TASK GROUPS",\n'
     '                    UiKit.Scroll(new TaskGroupListView(_services)), 640, 520)),'),
    # The status line has to be in the tree, not just assigned to.
    ('        footer.Children.Add(left);\n        footer.Children.Add(middle);\n        footer.Children.Add(right);\n        return footer;',
     '        footer.Children.Add(left);\n        footer.Children.Add(middle);\n        footer.Children.Add(right);\n\n'
     '        var stack = new StackPanel { Spacing = 4 };\n'
     '        stack.Children.Add(footer);\n'
     '        // A status line that only ever gets assigned to and never added is the R55 shape;\n'
     '        // it lives in the footer where the eye already is.\n'
     '        stack.Children.Add(new Border { Padding = new Thickness(12, 0, 12, 6), Child = _status });\n'
     '        return stack;'),
]

for old, new in subs:
    if old not in t:
        raise SystemExit("missing: " + old[:60])
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched TaskView")
