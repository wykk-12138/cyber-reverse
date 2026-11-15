import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 302 轮：`SmartActionsCreator.UseTemplate` —— A 类最后一个"可做"的做完了（33 → 32）

### 一、先查证据：模板在池子里是什么形态

```
PublishTemplate.* 键 9 个：Header / Title / TitlePlaceholder / Description /
                          DescriptionPlaceholder / Group / GroupPlaceholder / Publish / Error.NoTitle
SmartActions.Template.*   0 个
```

结论：**原版有"发布模板"这个功能**（复刻件其实早就写了 `PublishTemplateModal`，我 grep 键名时又漏了），
但**没有**"SmartAction 模板"这一层键 —— 所以模板来源只能是复刻件自己的 `SmartActionsDocument.Templates`。

### 二、我第一次又猜错了 API（三处）

```csharp
_services.SmartActions.Templates      → 不存在（引擎上没有）
template.Filters / template.Actions   → PublishedTemplate 只有元数据
new SmartActionFilterInput { Name = … } → 字段是 Filter / Input
```

**这是 R259 那条"先读那一行"的又一次破防。** 读了模型后才发现：

`PublishedTemplate` = `Id / Title / Description / Group / SourceActionId / PublishedUtc` —— **模板只带元数据**，
它指向"发布自哪个动作"（`SourceActionId`）。所以"用模板"= 顺着这个 id 把源动作的 filters 和 steps 复制过来。

### 三、最终实现（按真实形状）

```csharp
public bool UseTemplate(string title)   // 找到模板 → 顺着 SourceActionId 找源动作 → 复制 filters + steps
public IReadOnlyList<PublishedTemplate> Templates => _services.Config.SmartActions.Templates;
```

动作名不动（模板只是起点），复制后按当前页 `Navigate(...)` 重绘。

### 四、验证

```
绑定缺口    33 → **32**（real = ceiling = 账本标题）
相关测试    39 通过 / 0 失败
完整套件    1458 通过 / 0 失败 / 2 跳过（21 s）
```

### 五、这一轮的一句话

> A 类"可做"的到这一轮**清零**（剩 1 个 `OpenTracking` 缺运单来源、`OpenRelease` 不可得）。

> 而这轮又栽在"没先读模型"上 —— **我明明刚写过这条规矩，还是先写了代码。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 302 轮（`UseTemplate` 落地，缺口 **33 → 32**；A 类"可做"清零）。

---

## 缺口 32 = 1 可做 + 31 结构

| 类 | 数 | 内容 |
|---|---|---|
| A | 1 | `CheckoutView.OpenTracking`（缺运单链接来源） |
| — | (1) | `AnalyticsView.OpenRelease` —— **不可得** |
| B | 31 | 结构差异（`docs/BINDING_BACKLOG.md`） |

`UseTemplate` 的实现要点：`PublishedTemplate` **只带元数据**（`Id/Title/Description/Group/SourceActionId/PublishedUtc`），
"用模板"= 顺着 `SourceActionId` 复制源动作的 filters + steps；动作名不动。

**又一次破防**：我先猜了三处 API（`_services.SmartActions.Templates`、`template.Filters`、`SmartActionFilterInput.Name`），
全错。**规矩是"先读那一行"，我又先写了代码。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R302）
mutation   24/24 fired（R286）
Commit     26.3 GB / 可用 13.2 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
