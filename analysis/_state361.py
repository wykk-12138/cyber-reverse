import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 361 轮：`Solver` 四个 + `CaptchaProvider` 三个（类型级缺口 25 → 23）

| 类型 | 成员 |
|---|---|
| `Solver` | `Name` / `Captcha` / `View` / `Reload`（+ `RequestReload()` 动作） |
| `CaptchaProvider` | `Count` / `BalanceSupported` / `IsFetchingBalance` |

### 一个发现：两个"同类"记录字段不对等

`CloudflareSolverConfig` 早就有 `Count` 与 `BalanceSupported`，而 `CaptchaProvider` 一个都没有 ——
所以两个列表**没法用同一套列渲染**。这一轮补齐后它们对等了。

### 守卫帮了忙

我第一版脚本想同时给两个类加字段，`assert 'public int Count' not in t2` **挡住了重复添加**
（那两个字段本来就在 `CloudflareSolverConfig` 上）。**断言不是形式，它替我看见了"已经有"。**

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 25 → 23
```
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 361 轮（`Solver` 四成员 + `CaptchaProvider` 三字段；类型级缺口 25 → 23）。

---

## 模型层两个"同类记录"现在对等了

| 字段 | `CloudflareSolverConfig` | `CaptchaProvider` |
|---|---|---|
| `Count` | 原有 | **R361 补** |
| `BalanceSupported` | 原有 | **R361 补** |
| `IsFetchingBalance` | — | **R361 补** |

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 23（类型级，起点 52）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
