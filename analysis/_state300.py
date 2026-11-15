import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 300 轮：设置页导航 —— 池子说 16 个，复刻件有 15 个，**而 16 才是错的那一边**

### 一、发现

池子里有 **16 个 `Settings.Nav.*`** 文案键（Advanced / Appearance / CaptchaProviders / CloudflareSolvers /
CustomSizes / CustomStores / Data / EmailAccounts / General / GoogleAccounts / KeyboardShortcuts / NeedHelp /
Notifications / PayPalAccounts / Payment / Webhooks）。

复刻件的 `SettingsShell.Sections` 只有 **15** 个 —— 差的正是 `Advanced`。
而 `AdvancedView` 这个类**是存在的**，所以我判定："又一个死视图，把它接进导航"。

### 二、改完立刻红了四条

```
SummaryBlockTests.UiCountsInTheGuideMatchTheScan
UnreachedUiTypesTests.EveryBaselineEntryIsStillUnreachable
SettingsShellTests.SectionCountMatchesTheLiveRail
SettingsShellTests.AdvancedIsAGroupCaptionNotAPage   ← 关键
```

读那条守卫：

```csharp
// The live build prints "ADVANCED" as a caption above Captcha Providers. It is not
// navigable, so it must not appear as a section.
Assert.DoesNotContain(SettingsShell.Sections, s => s.Id == "advanced");
```

**原版把 "ADVANCED" 印成 Captcha Providers 上方的小标题，它不可点击。**
所以 16 个 `Settings.Nav.*` 里，15 个是页面、1 个是**分组标题**。

### 三、我错在哪

我把"池子里有 16 个导航文案"直接读成"有 16 个页面"。**文案数量 ≠ 可导航项数量。**
而这条知识早就被一条守卫写下来了 —— 是我没先看守卫，就先动手。

### 四、处理

- 源码改动**已回退**（不保留这个 section）；
- 我的新测试改成正确的形态：**15 个页面 + 1 个 `ADVANCED` 标题**（`s.Group == "ADVANCED"`）；
- 这条测试的价值反过来：它把"16 个文案 ↔ 15 页面 + 1 标题"这个映射钉住了。

### 五、验证

```
完整套件   1458 通过 / 0 失败 / 2 跳过（20 s）
```

### 六、这一轮的一句话

> 这一轮我"修"了一个不存在的缺陷，然后被**三年前（其实是几十轮前）的自己**写的守卫拦下来了。

> **动手前先读守卫 —— 它记着的知识，正是我此刻缺的那一条。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 300 轮（设置导航：**16 个 Nav 文案 = 15 页面 + 1 个 ADVANCED 标题**；我的"修复"已回退）。

---

## 一条重要教训（比本轮产出更重要）

池子里 **16 个 `Settings.Nav.*`** ≠ **16 个页面**：

| 项 | 数量 |
|---|---|
| `Settings.Nav.*` 文案 | 16 |
| 可导航页面 | **15** |
| `ADVANCED`（印在 Captcha Providers 上方的小标题，不可点） | 1 |

我一度把 `Advanced` 加成第 16 个 section，被 `SettingsShellTests.AdvancedIsAGroupCaptionNotAPage` 拦住
（连带红 4 条）。**源码改动已回退**，我的新测试改为正确形态（15 页面 + `s.Group == "ADVANCED"`）。

> **动手前先读守卫 —— 它记着的知识，正是我此刻缺的那一条。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R300）
mutation   24/24 fired（R286）
Commit     24.39 GB / 可用 14.17 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
