import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 249 轮（**纠正假数字：真实缺口 28 → 96**；注释被当成了代码；两个实现首次对齐）。

---

## ⚠ 缺口数字被修正：**real = 96**（不是 28）

**原因**：匹配器做"全文词边界匹配"，而这些年轮的注释里不断出现原版成员名（"原版在这里绑定 CopyAccounts"…），
**注释替代码顶了包**。剥掉注释后 real 从 28 跳到 96。

**两次修正才稳定**：第一版剥注释连 `https://…` 里的 `//` 一起吃了；改成 `(?<!:)//` 之后，
C# 棘轮与 `tools/bind_diff.py` **都给 96**（两个独立实现首次一致）。

**铁律**：
> 名字出现在注释里，证明的是"我知道它叫什么"，不是"我实现了它"。

## 真实 backlog（96，去噪 12 后）

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7（AddAction/AddInput/DeleteAction/DeleteInput/DeleteParam/ToggleFilterBehaviour/UseTemplate） |
| `Profiles.ProfileView` | 6（CreateGroup/CreateTest/MoveGroup/OpenCreator/OpenCsvEditor/OpenSettings） |
| `ProxyView` | 5（CreateGroup/MoveGroup/OpenSettings/ProxyTesters/TestAllKeybind） |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `TaskView` | 各 3 |
| 其余十余个类型 | 各 1–2 |

**棘轮**：`MaxRealGap = 96`（本轮重设基线；此前 28 是错的）。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
