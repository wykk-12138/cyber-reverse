import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ListPageColumnsTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Ui.Views;', 'using Cybersole.Ui.Views;\nusing Cybersole.Ui.Views.Proxies;\nusing Cybersole.Ui.Views.Tasks;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('usings added')
