import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 409 轮·勘误：我说"计数文案清完了"，其实只清完了**带 Loaded/Selected 的那一批**

### 一、我当时错在哪

我把统计口径限定在 `Loaded*/Count*/Selected*/GroupsLoaded*` 这 31 个键上，然后宣布"清零"。
但同一类文案还有两族没进这个正则：

```
python tools/locale_text_gap.py ProfileCsv   → 42 键，33 个原文不在源码里
python tools/locale_text_gap.py Utilities    → 23 键，14 个原文不在源码里
```

### 二、本轮补的（`Utilities.StoreGroups` 的三态）

```
CountNone   No stores
CountOne    1 store
CountFormat {0} stores
```

`StoresCount(n)` 现在是 `switch`：0 → "No stores"，1 → "1 store"，其余 `"{0} stores"`。
（`CountOne` 在池子里被截成 `"1 "`，名词部分由 `CountFormat` 的 "stores" 推出单数 "store"。）

### 三、还没清的

`ProfileCsv`（33）与 `Utilities`（其余 12）—— 已列入下一批，不在此声称"清零"。

```
PageCopyTests   21 通过 / 0 失败
```

### 四、这一轮的一句话

> 同一个错误今天第二次：**先限定口径，再宣布清零。**

> **"清零"只有在口径覆盖了全部同类项时才成立；否则它只是"这一口径下清零"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT corrigendum appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('文案缺口   Accounts/Proxies/Tasks/Profiles 四区清零；计数文案零态已补齐；Settings 21 条近似错误待核对',
                '文案缺口   Accounts/Proxies/Tasks/Profiles 四区清零；Loaded/Selected 计数文案清零；**ProfileCsv 33 条 / Utilities 12 条待补**；Settings 21 条近似错误待核对')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
