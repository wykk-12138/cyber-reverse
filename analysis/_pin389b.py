import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('            var missing = fields.Where(f => !props.Contains(f)).ToList();',
              '            // both sides case-folded: the image writes camelCase, C# properties are PascalCase\n'
              '            var missing = fields.Where(f => !props.Contains(f.ToLowerInvariant())).ToList();', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('case folded')
