import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 375 轮：`AnalyticsView.OpenRelease` —— 又一个"没被接上"的视图

### 一、工具先出活

新工具 `tools/wire_candidates.py`：把"没有任何地方构造的 UI 类"与"绑定表里 `Show*`/`Open*` 成员"做名字匹配。

```
不可达 UI 类 27
能对上名字的 Show*/Open* 绑定成员 15
```

排在前面的都是已经接好的（`TaskView.OpenTaskCreator` 等），但 **`AnalyticsView.OpenRelease → ReleaseView`** 是真的没实现。

### 二、补的成员

```csharp
public bool OpenRelease(Release release)   // 打开 ReleaseView，标题用 release.Product
```

`ReleaseView` 原本绑着 Previous / Release / ShowGuide / ShowSitelist，却**没有任何地方构造它**。
接上之后：不可达 29 → **28**。

### 三、验证

```
完整套件   1534 通过 / 0 失败 / 2 跳过
类型级缺口 16（AnalyticsView 还差别的成员，所以类型数未减）
```

### 四、这一轮的一句话

> 三页文档里都写着 `ReleaseView`，代码里没有一处 `new ReleaseView(` —— **文档说"有"，代码说"没人用"。**

> **"存在"和"被用到"是两个指标；后者才决定它是不是死的。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 375 轮（`AnalyticsView.OpenRelease`；不可达 UI 类 29 → 28；新增 `tools/wire_candidates.py`）。

---

## 新工具：`tools/wire_candidates.py`

列出"没有任何地方构造的 UI 类"与"绑定表里 `Show*`/`Open*` 成员"的名字匹配 —— **接线的候选队列**。

本轮据此补了 `AnalyticsView.OpenRelease`（`ReleaseView` 因此可达）。

## 剩余 16 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit/FetchBalance` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` ·
`GroupSummary.Clone/Delete/Edit` · `TaskView.Toggle` · `StoreGroupModal.Delete/IsEditing`

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 16（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
