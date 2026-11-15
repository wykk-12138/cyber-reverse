import io, re
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\DocsConsistencyTests.cs"
t = io.open(p, encoding='utf-8').read()
i = t.index('var claims = Regex.Matches(doc')
print(repr(t[i:i+140]))
