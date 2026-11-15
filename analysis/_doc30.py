import io
for path, old, new in [
    (r"D:\projects\cyber-reverse\replica\docs\RESUME.md",
     "| 不可达 UI 类 | **31**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |",
     "| 不可达 UI 类 | **30**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |"),
    (r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md",
     "UI 类      104 声明 / 31 不可达（PARITY.md 的 84 是另一个分母）",
     "UI 类      104 声明 / 30 不可达（PARITY.md 的 84 是另一个分母）"),
    (r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
     "| UI 类 | 104 个，**31 个不可达**（30%） | `UnreachedUiTypesTests` |",
     "| UI 类 | 104 个，**30 个不可达**（29%） | `UnreachedUiTypesTests` |"),
]:
    t = io.open(path, encoding='utf-8').read()
    if old in t:
        io.open(path, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
        print('updated', path.split('\\')[-1])
    else:
        print('pattern missing in', path.split('\\')[-1])
