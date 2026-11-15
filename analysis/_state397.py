import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 397 轮：接线时发现**两个空状态被我当成一个**

### 一、想做的事

把 Accounts 页的两条常量接到控件上：
`NoResultsSubtitle` 与 `GroupsLoaded(n)`。

### 二、第一个立刻踩雷

守卫 `TheAccountsRailIsATwoLevelTreeSoItDoesNotUseTheGrid` 红了：
它断言源码里存在 `"No stores matched your search"` —— 我把这行换成了 `NoResultsSubtitle`。

**这不是守卫过时，是我看错了**：原版有两个空状态：

| locale 键 | 原文 | 位置 |
|---|---|---|
| `Accounts.Empty.NoStores.Subtitle` | `No stores matched your search` | **左栏店铺搜索** |
| `Accounts.Empty.NoResults.Subtitle` | `There are no accounts matching your search` | **账户列表搜索结果** |

我把"店铺"那条换成了"账户"的文案 —— **界面上会变成一句答非所问的话**。

已回滚该行，保留原来的店铺文案。

### 三、成功的部分

左栏底部原本写的是 `LoadedCaption(group.Accounts.Count)`（**账户数**），
而原版这里是 `Accounts.GroupsLoaded*`（**组数**）→ 改为 `GroupsLoaded(_doc.AccountGroups.Count)`。

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 同一个页面里两处"空空如也"，文案完全不同 —— **常量名相似，语义相反。**

> **替换文案之前先问：这句话说的是哪个列表？**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 397 轮（Accounts 左栏底部改为"组数"；发现两个空状态被我混淆并回滚）。

---

## 两个空状态（别再混）

| 键 | 原文 | 用在哪 |
|---|---|---|
| `Accounts.Empty.NoStores.Subtitle` | `No stores matched your search` | 左栏店铺搜索 |
| `Accounts.Empty.NoResults.Subtitle` | `There are no accounts matching your search` | 账户列表搜索 |

守卫 `TheAccountsRailIsATwoLevelTreeSoItDoesNotUseTheGrid` 会盯着第一条的字面量。

## 已接线 / 待接线

| 区域 | 状态 |
|---|---|
| TaskGroup | ✅ 标签已接（R396） |
| Accounts | 部分（组数已接；空状态待接第二条） |
| Proxies / Tasks / Profiles | 常量已加，控件未接 |

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
