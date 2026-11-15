import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('var missing = names.Where(n => !props.Contains(n)).ToList();',
              'var missing = names.Where(n => !props.Contains(n.ToLowerInvariant())).ToList();')
t = t.replace('Assert.Empty(solver.Where(n => !solverProps.Contains(n)).ToList());',
              'Assert.Empty(solver.Where(n => !solverProps.Contains(n.ToLowerInvariant())).ToList());')
t = t.replace('Assert.Empty(settings.Where(n => !settingsProps.Contains(n)).ToList());',
              'Assert.Empty(settings.Where(n => !settingsProps.Contains(n.ToLowerInvariant())).ToList());')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('case-folded both sides')
