import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('"ReleaseView",', '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ReleaseView removed from the baseline')

for path, old, new in [
    (r"D:\projects\cyber-reverse\replica\docs\RESUME.md",
     "| 不可达 UI 类 | **29**", "| 不可达 UI 类 | **28**"),
    (r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md",
     "UI 类      104 声明 / 29 不可达", "UI 类      104 声明 / 28 不可达"),
    (r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
     "| UI 类 | 104 个，**29 个不可达**（28%） |", "| UI 类 | 104 个，**28 个不可达**（27%） |"),
]:
    t2 = io.open(path, encoding='utf-8').read()
    if old in t2:
        io.open(path, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
        print('updated', path.split('\\')[-1])
