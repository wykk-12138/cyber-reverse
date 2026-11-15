import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CopyTablesHygieneTests.cs"
t = io.open(p, encoding='utf-8').read()
print('braces:', t.count('{'), t.count('}'), '| parens:', t.count('('), t.count(')'))
i = t.index('TheTablesTogetherHold')
print(t[i-20:i+700])
