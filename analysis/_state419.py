import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 419 轮：`ProfileCreatorView` 六成员（缺口 10 → 9），但**测试没跑成**

### 一、补的（形状全部来自 `bind_shape.py`）

| 成员 | 形状 | 实现 |
|---|---|---|
| `Navigate` | get+set | 当前步骤名；设置时按名字选对应 tab |
| `Count` | get | `IsBulk ? Names.Count : 1` |
| `Profile` | get | 正在编辑的 `Profile` |
| `Names` | get | 名字列表 |
| `PaymentView` / `AdvancedView` | get | tab 已构建（两者同一条件） |

`Cybersole.Ui` 编译通过（`exit 0`），`bind_scope` 从 10 → **9 个类型**。

### 二、测试崩了（内存）

```
Commit 93.84 / 94.03 GB      available 0.87 GB
Testhost 进程已退出，但出现错误（无错误码）
```

**0.87 GB** —— 已经到这台机器的提交上限。测试进程直接崩，没有断言失败信息。

所以本轮结论是：

- **代码**：编译通过；
- **测试**：写了，**没跑成**（不是失败，是环境跑不动）。

### 三、留给下一轮

`SESSION_STATE.md` 顶部会写：内存恢复后先跑
`--filter "FullyQualifiedName~CloseAndOpenFamilyTests"`，确认 `Navigate` / `Count` / `Names` 的断言。

### 四、这一轮的一句话

> 同一件事我第三次区分"失败"和"没跑成" —— 这次连错误码都没有。

> **没有错误码的崩，比红色断言更容易被误读成"通过"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('## 当前状态')
head = '''## ⚠ 待验证（内存不足导致上一轮测试没跑成）

R419 给 `ProfileCreatorView` 加了 `Navigate / Count / Profile / Names / PaymentView / AdvancedView`
（编译通过），测试已写但 **testhost 在 0.87 GB 可用内存下崩溃**。内存恢复后先跑：

```
dotnet test tests/Cybersole.Tests -c Debug --no-restore -m:1 --filter "FullyQualifiedName~CloseAndOpenFamilyTests"
```

**当前 available 已低于 1 GB —— 建议先重启机器再继续。**

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE flagged with the pending test run')
