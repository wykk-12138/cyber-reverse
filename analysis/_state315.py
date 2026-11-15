import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 315 轮：补上 R314 欠的全套验证 —— 用 `--no-build` 把成本压到几乎为零

### 一、为什么能"不编译还跑全套"

R314 之后测试程序集已经是新的，所以可以用：

```bash
dotnet test --no-build --filter "Speed!=Slow"
```

**21 秒、可用内存只掉了 0.4 GB**（5.97 → 5.50）。在这个水位上，这是唯一还能做的"全套验证"。

### 二、结果：先红一条，再全绿

```
第一次：SummaryBlockTests.UiCountsInTheGuideMatchTheScan  [FAIL]
        UI classes: 99, unreachable: 30      vs  guide claims: 98 / 30
```

`ProfileCsvRow` 是 `Cybersole.Ui` 里的 public class，把**声明数**从 98 顶到 99；
但它**在 src 里被构造**（`ProfileCsvEditorView.Rows`），所以**不可达数仍是 30**。
改指南为「99 个，30 个不可达（30%）」后：

```
完整套件   1468 通过 / 0 失败 / 2 跳过（21 s，--no-build）
```

比 R312 的 1463 多 5 条 = `ProfileCsvRowTests`。

### 三、顺手确认三处计数都在同一条线上

- `UnreachedUiTypesTests`：30 未构造 / 基线 30 ✔（`ProfileCsvRow` 不在基线里，因为它被构造了）
- `SummaryBlockTests`：指南 **99 / 30** ✔
- `ParityDocTests`：`PARITY.md` 84（26 Window + 58 UserControl）不变 ✔ —— `ProfileCsvRow` 不是 UserControl

### 四、这一轮的一句话

> 我一直以为"全套验证 = 必须重新编译"。今天发现 `--no-build` 让它在 5.5 GB 水位上也能跑完。

> **资源紧的时候，先想"哪个成本可以省"，而不是"哪件事可以不做"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 315 轮（用 `--no-build` 在 5.5 GB 水位跑完全套：**1468 通过 / 0 失败 / 2 跳过**）。

---

## 低成本验证技巧（记下来）

```bash
dotnet test tests/Cybersole.Tests -c Debug --no-build --filter "Speed!=Slow"
```

只要测试程序集是新的，就**不需要重编译** —— 21 秒、内存只掉约 0.4 GB。
低内存时的首选验证方式。

## 当前数字（R315 时点，全套）

| 指标 | 值 |
|---|---|
| 完整套件 | **1468 通过 / 0 失败 / 2 跳过** |
| UI 类 | **99 声明 / 30 不可达** |
| `PARITY.md` | 84（26 Window + 58 UserControl） |
| 缺口 | **26**（real = ceiling = 账本标题） |
| mutation | 29 条 / 锚点 29/29 |

## 剩余 B 类 6 件

`FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（依据见 `docs/B_CLASS_DECISIONS.md`）。

## 状态

```
Commit 42.7 GB / 可用 5.5 GB   ← 低于硬线；重启后再做下一件
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
