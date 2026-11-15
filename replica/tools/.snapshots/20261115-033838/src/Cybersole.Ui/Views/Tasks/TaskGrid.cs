using Cybersole.Ui.Views.Common;

// ---------------------------------------------------------------------------------------------------------------
// R209 note: this file was truncated to zero bytes by a bad script during round 209 and was restored by
// decompiling this project's own last good build (src/Cybersole.Ui/bin/Debug/net8.0/Cybersole.Ui.dll, built 16:02:30,
// ILSpy 8.2.0.7535). The code is the same code; the XML documentation comments are gone, and this header is the record.
// Lesson: never write a file from a PowerShell string operation -- a failed Replace yields $null and WriteAllText
// happily truncates the target.
// ---------------------------------------------------------------------------------------------------------------

﻿using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;

namespace Cybersole.Ui.Views.Tasks;

public sealed class TaskGrid : UserControl
{
	public enum TaskColumn
	{
		Site,
		Product,
		Profile,
		Proxies,
		Status
	}

	private readonly IList<BotTask> _rows;

	private readonly Action? _onChanged;

	private readonly List<BotTask> _selection = new List<BotTask>();

	private readonly List<(BotTask Task, Grid Row)> _rowVisuals = new List<(BotTask, Grid)>();

	private BotTask? _anchor;

	private TaskColumn _sortColumn = TaskColumn.Site;

	private bool _sortAscending = true;

	private string? _filter;

	private static readonly IBrush SelectionBrush = new SolidColorBrush(Color.Parse("#2A2E3A"));

	private Func<BotTask, TaskState>? _statusOf;

	private Action<IReadOnlyList<BotTask>>? _starter;

	private Action<IReadOnlyList<BotTask>>? _staggerStarter;

	private Action<IReadOnlyList<BotTask>>? _forceStarter;

	private Action? _stopper;

	private Action<BotTask>? _editor;

	private Action<IReadOnlyList<BotTask>>? _cloner;

	private Action<BotTask>? _viewer;

	private Action<BotTask>? _opener;

	private Action<IReadOnlyList<BotTask>>? _deleter;

	private Control? _headerActions;

	// R218: the four leading proportions are measured, not estimated. Header label left edges were read off the running
	// build at two window widths and agree exactly once normalised by the Proxies column:
	//
	//   width 1568:  Site 204  Product 384  Profile 191  Proxies 168
	//   width 1375:  Site 165  Product 311  Profile 155  Proxies 136
	//   ratio       :  1.21       2.29         1.14        1.00
	//
	// The replica had 1.3 / 2.2 / 1.2 / 1.2, i.e. Site and Proxies were both wrong by about 10%. Status stays at 1.1
	// on purpose: in an empty table the last star column absorbs the remainder, so its width measures the leftover
	// space rather than a designed proportion and cannot be inferred from these screenshots.
	private const string RowColumns = "34,1.21*,2.29*,1.14*,1.0*,1.1*,90";

	internal const string ActionsWidth = "90";

	public TaskColumn SortColumn => _sortColumn;

	public bool SortAscending => _sortAscending;

	public string? Filter => _filter;

	public IReadOnlyList<BotTask> SelectedTasks
	{
		get
		{
			_selection.RemoveAll((BotTask t) => !_rows.Contains(t));
			return _selection;
		}
	}

	internal bool AllSelected => _rows.Count > 0 && _rows.All(_selection.Contains);

	public TaskGrid(IList<BotTask> rows, Action? onChanged = null)
	{
		_rows = rows;
		_onChanged = onChanged;
		base.Content = Build();
	}

	private void Rebuild()
	{
		base.Content = Build();
	}

	private void PaintSelection()
	{
		foreach (var rowVisual in _rowVisuals)
		{
			BotTask item = rowVisual.Task;
			Grid item2 = rowVisual.Row;
			IBrush background;
			if (!_selection.Contains(item))
			{
				IBrush transparent = Brushes.Transparent;
				background = transparent;
			}
			else
			{
				background = SelectionBrush;
			}
			item2.Background = background;
		}
	}

	internal void SortBy(TaskColumn column)
	{
		if (_sortColumn == column)
		{
			_sortAscending = !_sortAscending;
		}
		else
		{
			_sortColumn = column;
			_sortAscending = true;
		}
		Rebuild();
	}

	internal List<BotTask> Ordered()
	{
		List<BotTask> source = (string.IsNullOrWhiteSpace(_filter) ? _rows.ToList() : _rows.Where((BotTask t) => Cell(t, TaskColumn.Site).Contains(_filter, StringComparison.OrdinalIgnoreCase) || Cell(t, TaskColumn.Product).Contains(_filter, StringComparison.OrdinalIgnoreCase) || Cell(t, TaskColumn.Status).Contains(_filter, StringComparison.OrdinalIgnoreCase)).ToList());
		TaskColumn sortColumn = _sortColumn;
		if (1 == 0)
		{
		}
		Func<BotTask, string> func = sortColumn switch
		{
			TaskColumn.Product => (BotTask t) => Cell(t, TaskColumn.Product), 
			TaskColumn.Profile => (BotTask t) => Cell(t, TaskColumn.Profile), 
			TaskColumn.Proxies => (BotTask t) => Cell(t, TaskColumn.Proxies), 
			TaskColumn.Status => (BotTask t) => Cell(t, TaskColumn.Status), 
			_ => (BotTask t) => Cell(t, TaskColumn.Site), 
		};
		if (1 == 0)
		{
		}
		Func<BotTask, string> keySelector = func;
		return (_sortAscending ? source.OrderBy<BotTask, string>(keySelector, StringComparer.OrdinalIgnoreCase) : source.OrderByDescending<BotTask, string>(keySelector, StringComparer.OrdinalIgnoreCase)).ToList();
	}

	internal string SortGlyph(TaskColumn column)
	{
		return (_sortColumn != column) ? string.Empty : (_sortAscending ? "↑" : "↓");
	}

	public TaskGrid SetFilter(string? filter)
	{
		_filter = filter;
		Rebuild();
		return this;
	}

	internal string Cell(BotTask task, TaskColumn column)
	{
		if (1 == 0)
		{
		}
		string result = column switch
		{
			TaskColumn.Product => string.IsNullOrWhiteSpace(task.Product?.Name) ? "—" : task.Product.Name, 
			TaskColumn.Profile => string.IsNullOrWhiteSpace(task.ProfileId) ? "—" : task.ProfileId, 
			TaskColumn.Proxies => string.IsNullOrWhiteSpace(task.ProxyGroupId) ? "—" : task.ProxyGroupId, 
			TaskColumn.Status => (_statusOf?.Invoke(task) ?? task.State).ToString(), 
			_ => string.IsNullOrWhiteSpace(task.Store) ? "—" : task.Store, 
		};
		if (1 == 0)
		{
		}
		return result;
	}

	public TaskGrid WithStatus(Func<BotTask, TaskState> statusOf)
	{
		_statusOf = statusOf;
		Rebuild();
		return this;
	}

	internal void SelectSingle(BotTask task)
	{
		_selection.Clear();
		_selection.Add(task);
		_anchor = task;
		PaintSelection();
	}

	internal void SelectToggle(BotTask task)
	{
		if (!_selection.Remove(task))
		{
			_selection.Add(task);
		}
		_anchor = task;
		PaintSelection();
	}

	internal void SelectRange(BotTask task)
	{
		List<BotTask> list = Ordered();
		BotTask item = ((_anchor != null && list.Contains(_anchor)) ? _anchor : task);
		int num = list.IndexOf(item);
		int num2 = list.IndexOf(task);
		if (num >= 0 && num2 >= 0)
		{
			_selection.Clear();
			for (int i = Math.Min(num, num2); i <= Math.Max(num, num2); i++)
			{
				_selection.Add(list[i]);
			}
			PaintSelection();
		}
	}

	internal void SelectForMenu(BotTask task)
	{
		if (!_selection.Contains(task))
		{
			_selection.Clear();
			_selection.Add(task);
			_anchor = task;
			PaintSelection();
		}
	}

	internal void SelectAll()
	{
		_selection.Clear();
		_selection.AddRange(_rows);
		_anchor = _rows.FirstOrDefault();
		Rebuild();
	}

	internal static string CountCaption(int count)
	{
		return $"{count} Tasks";
	}

	internal static string SelectionHeader(int count)
	{
		return (count == 1) ? "1 TASK SELECTED" : $"{count} TASKS SELECTED";
	}

	public TaskGrid WithStarter(Action<IReadOnlyList<BotTask>> start)
	{
		_starter = start;
		Rebuild();
		return this;
	}

	public TaskGrid WithStaggerStarter(Action<IReadOnlyList<BotTask>> start)
	{
		_staggerStarter = start;
		Rebuild();
		return this;
	}

	public TaskGrid WithForceStarter(Action<IReadOnlyList<BotTask>> start)
	{
		_forceStarter = start;
		Rebuild();
		return this;
	}

	public TaskGrid WithStopper(Action stop)
	{
		_stopper = stop;
		Rebuild();
		return this;
	}

	public TaskGrid WithEditor(Action<BotTask> edit)
	{
		_editor = edit;
		Rebuild();
		return this;
	}

	public TaskGrid WithCloner(Action<IReadOnlyList<BotTask>> clone)
	{
		_cloner = clone;
		Rebuild();
		return this;
	}

	public TaskGrid WithViewer(Action<BotTask> view)
	{
		_viewer = view;
		Rebuild();
		return this;
	}

	public TaskGrid WithOpener(Action<BotTask> open)
	{
		_opener = open;
		Rebuild();
		return this;
	}

	public TaskGrid WithDeleter(Action<IReadOnlyList<BotTask>> delete)
	{
		_deleter = delete;
		Rebuild();
		return this;
	}

	// R229: the hooks above were only reachable through the row menu. The original binds these as commands on the view
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

	internal List<object> MenuFor(IReadOnlyList<BotTask> selection)
	{
		IReadOnlyList<BotTask> selection2 = selection;
		int count = selection2.Count;
		List<object> list = new List<object>
		{
			new MenuItem
			{
				Header = SelectionHeader(count),
				IsEnabled = false
			}
		};
		if (_starter != null)
		{
			list.Add(Item("Start Tasks", delegate
			{
				_starter(selection2);
			}));
		}
		if (_staggerStarter != null)
		{
			list.Add(Item("Stagger Start Tasks", delegate
			{
				_staggerStarter(selection2);
			}));
		}
		if (_forceStarter != null)
		{
			list.Add(Item("Force Start Tasks", delegate
			{
				_forceStarter(selection2);
			}));
		}
		if (_stopper != null)
		{
			list.Add(Item("Stop Tasks", delegate
			{
				_stopper();
			}));
		}
		list.Add(new Separator());
		if (_editor != null)
		{
			list.Add(Item("Edit Tasks", delegate
			{
				_editor(selection2[0]);
			}));
		}
		if (_cloner != null)
		{
			list.Add(Item("Clone Tasks", delegate
			{
				_cloner(selection2);
			}));
		}
		if (count == 1 && _viewer != null)
		{
			list.Add(Item("View Task", delegate
			{
				_viewer(selection2[0]);
			}));
		}
		if (count == 1 && _opener != null)
		{
			list.Add(Item("Open In Browser", delegate
			{
				_opener(selection2[0]);
			}));
		}
		list.Add(new Separator());
		if (_deleter != null)
		{
			list.Add(Item("Delete Tasks", delegate
			{
				_deleter(selection2);
			}));
		}
		return list;
	}

	public TaskGrid WithHeaderActions(Control actions)
	{
		_headerActions = actions;
		Rebuild();
		return this;
	}

	/// <summary>The sortable columns, in the order the live page shows them (R331).</summary>
	internal static readonly string[] Headers = { "Site", "Product", "Profile", "Proxies", "Status" };

	/// <summary>The same columns as sort keys, positionally aligned with <see cref="Headers"/>.</summary>
	private static readonly TaskColumn[] HeaderColumns =
	{
		TaskColumn.Site, TaskColumn.Product, TaskColumn.Profile, TaskColumn.Proxies, TaskColumn.Status,
	};

	private Control Build()
	{
		Grid grid = new Grid
		{
			ColumnDefinitions = new ColumnDefinitions("34,1.3*,2.2*,1.2*,1.2*,1.1*,90"),
			Margin = new Thickness(4.0, 0.0, 4.0, 6.0)
		};
		CheckBox selectAll = new CheckBox
		{
			IsChecked = AllSelected,
			VerticalAlignment = VerticalAlignment.Center
		};
		selectAll.IsCheckedChanged += delegate
		{
			if (selectAll.IsChecked.GetValueOrDefault())
			{
				SelectAll();
			}
			else
			{
				_selection.Clear();
				PaintSelection();
			}
		};
		// R319: header cells are described as ElementCell, so the column rule is data instead of a repeated call.
		foreach (var cell in new[]
		         {
		             new ElementCell("select-all", selectAll, 0),
		             new ElementCell("header-actions", _headerActions, 6),
		         })
		{
			if (cell.Content is not Control control) continue;
			Grid.SetColumn(control, cell.Column);
			Grid.SetColumnSpan(control, cell.ColumnSpan);
		}

		Grid.SetColumn(selectAll, 0);
		grid.Children.Add(selectAll);
		// R333: the header row comes from one array, so the order the live page shows (R331) is data and testable.
		for (var i = 0; i < Headers.Length; i++)
			grid.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));
		if (_headerActions != null)
		{
			_headerActions.VerticalAlignment = VerticalAlignment.Center;
			Grid.SetColumn(_headerActions, 6);
			grid.Children.Add(_headerActions);
		}
		else
		{
			TextBlock textBlock = new TextBlock
			{
				Text = CountCaption(_rows.Count),
				FontWeight = FontWeight.DemiBold,
				VerticalAlignment = VerticalAlignment.Center,
				HorizontalAlignment = HorizontalAlignment.Right
			};
			Grid.SetColumn(textBlock, 6);
			grid.Children.Add(textBlock);
		}
		StackPanel stackPanel = new StackPanel
		{
			Spacing = 2.0
		};
		_rowVisuals.Clear();
		foreach (BotTask item in Ordered())
		{
			stackPanel.Children.Add(BuildRow(item));
		}
		if (_rows.Count == 0)
		{
			// R209: the shared EmptyView owns the glyph, the headline and this page's second line.
			EmptyView tasksEmpty = EmptyView.For("tasks");
			tasksEmpty.Margin = new Thickness(0.0, 60.0, 0.0, 0.0);
			stackPanel.Children.Add(tasksEmpty);
		}
		return new DockPanel
		{
			LastChildFill = true,
			Children = 
			{
				Docked(grid, Dock.Top),
				(Control)new ScrollViewer
				{
					Content = stackPanel
				}
			}
		};
	}

	private Control HeaderButton(string label, TaskColumn column, int gridColumn)
	{
		string text = SortGlyph(column);
		Button button = new Button
		{
			Content = new TextBlock
			{
				Text = ((text.Length == 0) ? label : (label + " " + text)),
				FontWeight = FontWeight.DemiBold,
				VerticalAlignment = VerticalAlignment.Center
			},
			Background = Brushes.Transparent,
			BorderThickness = new Thickness(0.0),
			Padding = new Thickness(4.0, 0.0),
			HorizontalAlignment = HorizontalAlignment.Left,
			HorizontalContentAlignment = HorizontalAlignment.Left
		};
		button.Click += delegate
		{
			SortBy(column);
		};
		Grid.SetColumn(button, gridColumn);
		return button;
	}

	private Control BuildRow(BotTask task)
	{
		BotTask task2 = task;
		Grid obj = new Grid
		{
			ColumnDefinitions = new ColumnDefinitions("34,1.3*,2.2*,1.2*,1.2*,1.1*,90"),
			Margin = new Thickness(4.0, 3.0, 4.0, 3.0)
		};
		IBrush background;
		if (!_selection.Contains(task2))
		{
			IBrush transparent = Brushes.Transparent;
			background = transparent;
		}
		else
		{
			background = SelectionBrush;
		}
		obj.Background = background;
		Grid row = obj;
		CheckBox check = new CheckBox
		{
			IsChecked = _selection.Contains(task2),
			VerticalAlignment = VerticalAlignment.Center
		};
		check.IsCheckedChanged += delegate
		{
			if (check.IsChecked.GetValueOrDefault())
			{
				SelectToggle(task2);
			}
			else if (_selection.Contains(task2))
			{
				SelectToggle(task2);
			}
		};
		Grid.SetColumn(check, 0);
		row.Children.Add(check);
		row.Children.Add(DataCell(task2, TaskColumn.Site, 1));
		row.Children.Add(DataCell(task2, TaskColumn.Product, 2));
		row.Children.Add(DataCell(task2, TaskColumn.Profile, 3));
		row.Children.Add(DataCell(task2, TaskColumn.Proxies, 4));
		row.Children.Add(DataCell(task2, TaskColumn.Status, 5));
		row.PointerPressed += delegate(object? _, PointerPressedEventArgs e)
		{
			if (e.GetCurrentPoint(row).Properties.IsLeftButtonPressed)
			{
				if (e.KeyModifiers.HasFlag(KeyModifiers.Shift))
				{
					SelectRange(task2);
				}
				else if (e.KeyModifiers.HasFlag(KeyModifiers.Control))
				{
					SelectToggle(task2);
				}
				else
				{
					SelectSingle(task2);
				}
			}
		};
		ContextMenu menu = new ContextMenu
		{
			ItemsSource = MenuFor(new BotTask[1] { task2 })
		};
		menu.Opening += delegate
		{
			SelectForMenu(task2);
			ContextMenu contextMenu = menu;
			TaskGrid taskGrid = this;
			IReadOnlyList<BotTask> selection;
			if (SelectedTasks.Count <= 0)
			{
				IReadOnlyList<BotTask> readOnlyList = new BotTask[1] { task2 };
				selection = readOnlyList;
			}
			else
			{
				selection = SelectedTasks;
			}
			contextMenu.ItemsSource = taskGrid.MenuFor(selection);
		};
		row.ContextMenu = menu;
		_rowVisuals.Add((task2, row));
		return row;
	}

	private TextBlock DataCell(BotTask task, TaskColumn column, int gridColumn)
	{
		TextBlock textBlock = new TextBlock
		{
			Text = Cell(task, column),
			VerticalAlignment = VerticalAlignment.Center,
			TextTrimming = TextTrimming.CharacterEllipsis
		};
		Grid.SetColumn(textBlock, gridColumn);
		return textBlock;
	}

	private static MenuItem Item(string header, Action action)
	{
		Action action2 = action;
		MenuItem menuItem = new MenuItem
		{
			Header = header
		};
		menuItem.Click += delegate
		{
			action2();
		};
		return menuItem;
	}

	private static Control Docked(Control control, Dock dock)
	{
		DockPanel.SetDock(control, dock);
		return control;
	}
}
