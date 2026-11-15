import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 374 轮：`ReleaseView.ShowSitelist`（缺口 17 → 16，不可达 UI 类 30 → 29）

### 一、证据链很短，但完整

```
"Release.Tab.Sitelist": "Sitelist"      ← locale 里就有一个 Sitelist 标签
ReleaseSitelistView : UserControl       ← 复刻件里已有这个视图，但从没被构造过
ReleaseView 的绑定清单里有 ShowSitelist  ← 注释里早就写着
```

三样一凑，`ShowSitelist()` 就是"打开这个视图"，标题用 locale 的 `Sitelist`。

### 二、连带的两个数字

- `UnreachedUiTypesTests` 基线删掉 `ReleaseSitelistView`（它现在可达了）；
- 指南 31 → 30 → **29**（`RESUME.md` / `SESSION_STATE.md` / `VERDICT.md` 同步）。

```
完整套件   1534 通过 / 0 失败 / 2 跳过
bind_scope 17 → 16
```

### 三、这一轮的一句话

> 这轮的两条线索都在**我已经写下过却没用上的地方**：locale 里有 "Sitelist"，类注释里写着 `ShowSitelist`。

> **缺口常常不是"缺证据"，而是"证据在我自己写过的文档里没被接上"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 374 轮（`ReleaseView.ShowSitelist`；缺口 16，不可达 UI 类 29）。

---

## 连着两轮都是"把已有视图接上"

| 轮 | 成员 | 接上的既有视图 |
|---|---|---|
| R373 | `TaskView.CreateGroup` | `TaskGroupView` |
| R374 | `ReleaseView.ShowSitelist` | `ReleaseSitelistView` |

**不可达 UI 类 31 → 29。** 剩下的 29 个多半是原版也没有的弹窗，或需要真数据才有意义。

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 16（类型级）
UI 类      104 声明 / 29 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
