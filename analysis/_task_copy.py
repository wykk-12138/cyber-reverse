import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    public TaskGroup? SelectedGroup => _group;'''
add = '''    // ------------------------------------------------ copy from the image's locale (R394)

    /// <summary>"Copy URL" — the task context menu's copy entry.</summary>
    public const string ContextCopyUrl = "Copy URL";

    /// <summary>"Move tasks to" — the context menu's move entry.</summary>
    public const string ContextMoveTo = "Move tasks to";

    /// <summary>"Delete {0} tasks?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} tasks?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} tasks?\\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) tasks" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) tasks";

    /// <summary>Shown when a search matches no task.</summary>
    public const string NoResultsSubtitle = "There are no tasks matching your search";

    /// <summary>"Multiple Products ({0})" — the product column when a task watches several.</summary>
    public const string MultipleProductsFormat = "Multiple Products ({0})";

    /// <summary>"{0} Selected" — the grid's own counter.</summary>
    public const string SelectedFormat = "{0} Selected";

    /// <summary>"{0} TASKS SELECTED" — the page's selection counter.</summary>
    public const string SelectedManyFormat = "{0} TASKS SELECTED";

    /// <summary>"{0} TASK SELECTED" — the singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} TASK SELECTED";

    /// <summary>The product column's text for a task watching <paramref name="count"/> products.</summary>
    public static string ProductsCaption(int count) =>
        count == 1 ? "(one product)" : string.Format(MultipleProductsFormat, count);

    /// <summary>The page's selection counter, singular when one task is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

    /// <summary>The grid's own counter.</summary>
    public static string GridSelected(int count) => string.Format(SelectedFormat, count);

''' + anchor
assert anchor in t and 'SelectedOneFormat' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ten task strings added')
