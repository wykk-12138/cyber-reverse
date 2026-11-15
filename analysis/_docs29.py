import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('"CheckoutList", "CheckoutView", "ReleaseSitelistView"', '"CheckoutList", "CheckoutView"', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ReleaseSitelistView removed from the unreachable baseline')

for path, old, new in [
    (r"D:\projects\cyber-reverse\replica\docs\RESUME.md",
     "| 不可达 UI 类 | **30**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |",
     "| 不可达 UI 类 | **29**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |"),
    (r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md",
     "UI 类      104 声明 / 30 不可达（PARITY.md 的 84 是另一个分母）",
     "UI 类      104 声明 / 29 不可达（PARITY.md 的 84 是另一个分母）"),
    (r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
     "| UI 类 | 104 个，**30 个不可达**（29%） | `UnreachedUiTypesTests` |",
     "| UI 类 | 104 个，**29 个不可达**（28%） | `UnreachedUiTypesTests` |"),
]:
    t2 = io.open(path, encoding='utf-8').read()
    if old in t2:
        io.open(path, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
        print('updated', path.split('\\')[-1])
