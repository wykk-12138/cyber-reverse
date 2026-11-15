import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LoginControlTests.cs"
t = io.open(p, encoding='utf-8').read()
print('existing tests:', t.count('[Fact]'), '[Theory]', t.count('[Theory]'))
print(t[:600])
