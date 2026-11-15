import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('"TaskCreatorView", "TaskGroupView", "GroupSummary",', '"TaskCreatorView", "GroupSummary",', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskGroupView removed from the unreachable baseline (TaskView.CreateGroup now constructs it)')
