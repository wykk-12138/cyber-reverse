import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 253 轮（MessageBoxDialog 4 + ProfileCreatorView 4；缺口 64；守卫第四次抓到我；89 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 64`

## 死字段守卫已抓到我四次

| 轮次 | 字段 | 后果 |
|---|---|---|
| R243 | `_appearanceServices` | `ResetDefaults()` 永远提前返回（我自查发现） |
| R244 | `ProviderViews._services`、`_dataServices` | `RefreshProviders()` 恒返回 / 字段从未使用 |
| R253 | `ProfileCreatorView._saved` | `IsCreating` 永远是 true |

**结论**：这类错误编译器看不见、行为测试覆盖不到，**只能靠静态规则拦**。

## 剩余 64 的头部

| 类型 | 缺 |
|---|---|
| `Attributes.Platform` | 3（**已知不可得**） |
| `ProfileCsvRow` / `FilterRow` | 各 3（行控件不存在） |
| `AccountGrid` / `AnalyticsView` / `Platform` / 其他 | 各 2 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
