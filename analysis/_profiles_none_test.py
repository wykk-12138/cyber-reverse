import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''    [InlineData(0, "0 Profiles Loaded")]''', '''    [InlineData(0, "No Profiles Loaded")]''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('the zero case now expects the image wording')
