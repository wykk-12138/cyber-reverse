import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 326 轮：发现两个"UI 类"数字其实**分母不同**，而不是有一个错了（不编译）

### 一、差点做错事

顺手对账时看到：

| 文档 | 数字 |
|---|---|
| `PARITY.md` | **84** 个 UI 类（26 `Window` + 58 `UserControl`） |
| 指南 / `RESUME.md` | **104** 个声明、**31** 个不可达 |

第一反应是"哪个错了"。查了两条守卫的判定口径才明白：

| 守卫 | 数什么 | 结果 |
|---|---|---|
| `ParityDocTests.TheUiClassCountsInParityMatchTheSource` | 只数 `class X : Window` / `: UserControl` | 84 |
| `UnreachedUiTypesTests` | `Cybersole.Ui` 里**所有 public class** | 104（31 未构造） |

**两个都对**，只是分母不同：一个是"窗口/控件"，一个是"全部 UI 类型"。

### 二、处理方式：写清口径，不去对齐

- `PARITY.md` 的 84 后面加了口径说明；
- `RESUME.md` 拆成两行，各自标出分母。

**没有改任何数字** —— 因为改了才是真错。

### 三、验证

```
ParityDocTests + SummaryBlockTests   13 通过 / 0 失败（--no-build）
```

### 四、这一轮的一句话

> 对账最危险的一步不是"发现不一致"，而是**"发现不一致就立刻去改一个"**。

> **先问"它们数的是不是同一个东西"，再决定要不要动。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 326 轮（把两个"UI 类"分母写清：84 = Window/UserControl，104 = 全部 public class；未改数字）。

---

## 两个分母（别再试图对齐）

| 指标 | 值 | 数什么 |
|---|---|---|
| `PARITY.md` UI 类 | **84**（26 + 58） | 只数 `Window` / `UserControl` 子类 |
| 指南 / RESUME 不可达 | **31 / 104** | `Cybersole.Ui` 里所有 public class |

两处都已在文档里标注分母。**数字没改** —— 改了才是真错。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径，real = ceiling = 账本标题）
Commit     44.5 GB / 可用 4.6 GB   ← 低于硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
