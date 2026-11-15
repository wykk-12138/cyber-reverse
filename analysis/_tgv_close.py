import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Removes this group from the configuration (bound as <c>Delete</c>). False when it was never saved.</summary>'''
add = '''    /// <summary>
    /// Closes the hosting dialog (bound as <c>Close</c>). False when this control is not inside a window, which is what a
    /// test that builds the view without a host sees.
    /// </summary>
    public bool Close()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('Close added')
