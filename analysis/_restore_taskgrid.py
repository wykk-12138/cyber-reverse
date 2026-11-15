import io
src = io.open(r'D:\projects\cyber-reverse\analysis\_recovered_TaskGrid.cs', encoding='utf-8').read()

header = '''using Cybersole.Ui.Views.Common;

// ---------------------------------------------------------------------------------------------------------------
// R209 note: this file was truncated to zero bytes by a bad script during round 209 and was restored by
// decompiling this project's own last good build (src/Cybersole.Ui/bin/Debug/net8.0/Cybersole.Ui.dll, built 16:02:30,
// ILSpy 8.2.0.7535). The code is the same code; the XML documentation comments are gone, and this header is the record.
// Lesson: never write a file from a PowerShell string operation -- a failed Replace yields $null and WriteAllText
// happily truncates the target.
// ---------------------------------------------------------------------------------------------------------------

'''

old = '''			stackPanel.Children.Add(new StackPanel
			{
				Spacing = 4.0,
				Margin = new Thickness(0.0, 60.0, 0.0, 0.0),
				HorizontalAlignment = HorizontalAlignment.Center,
				Children = 
				{
					(Control)new TextBlock
					{
						Text = "Nothing to see here",
						FontSize = 18.0,
						FontWeight = FontWeight.DemiBold,
						HorizontalAlignment = HorizontalAlignment.Center
					},
					(Control)new TextBlock
					{
						Text = "Add some tasks to get started",
						Opacity = 0.6,
						HorizontalAlignment = HorizontalAlignment.Center
					}
				}
			});'''

new = '''			// R209: the shared EmptyView owns the glyph, the headline and this page's second line.
			EmptyView tasksEmpty = EmptyView.For("tasks");
			tasksEmpty.Margin = new Thickness(0.0, 60.0, 0.0, 0.0);
			stackPanel.Children.Add(tasksEmpty);'''

assert old in src, 'empty block not found in recovered source'
out = header + src.replace(old, new)
io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs', 'w', encoding='utf-8', newline='').write(out)
print('restored', len(out), 'bytes')
