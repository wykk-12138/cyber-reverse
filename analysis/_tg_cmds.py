import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''	internal List<object> MenuFor(IReadOnlyList<BotTask> selection)'''
add = '''	// R229: the hooks above were only reachable through the row menu. The original binds these as commands on the view
	// (`StartSelected`, `ForceStartSelected`, `OpenStaggerStart`, `EditSelected`, `CloneSelected`, `OpenTaskView`,
	// `OpenBrowser`, `DeleteSelected` — analysis/xaml_bindings.json), so the same behaviour gets a named entry point
	// here, which the view then exposes. One implementation, two ways in.

	internal void StartSelectedTasks() { if (_starter is null) return; _starter(EffectiveSelection()); }

	internal void StaggerStartSelectedTasks() { if (_staggerStarter is null) return; _staggerStarter(EffectiveSelection()); }

	internal void ForceStartSelectedTasks() { if (_forceStarter is null) return; _forceStarter(EffectiveSelection()); }

	internal void StopSelectedTasks() => _stopper?.Invoke();

	internal void EditSelectedTasks()
	{
		var first = EffectiveSelection().FirstOrDefault();
		if (first is not null) _editor?.Invoke(first);
	}

	internal void CloneSelectedTasks() { if (_cloner is not null) _cloner(EffectiveSelection()); }

	internal void ViewSelectedTask()
	{
		var first = EffectiveSelection().FirstOrDefault();
		if (first is not null) _viewer?.Invoke(first);
	}

	internal void OpenSelectedTask()
	{
		var first = EffectiveSelection().FirstOrDefault();
		if (first is not null) _opener?.Invoke(first);
	}

	internal void DeleteSelectedTasks() { if (_deleter is not null) _deleter(EffectiveSelection()); }

	/// <summary>The selection, or every visible row when nothing is selected — the same rule the buttons used.</summary>
	internal IReadOnlyList<BotTask> EffectiveSelection()
	{
		var picked = SelectedTasks.ToList();
		return picked.Count > 0 ? picked : Ordered();
	}

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskGrid named entry points added')
