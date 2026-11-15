import io
p = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## §10 绑定缺口的口径有一个盲点（R342）

名字级口径（`tools/bind_diff.py`）问的是"整个仓库里有没有这个名字"，
所以**成员挂错类型也算满足**：

- `IWebhook` 应带 `Events` / `Type`，而复刻件的 `IWebhook` 只有 `ExtraFields` —— 但 `Events`、`Type`
  在 `TaskGroup` / 别处已有，**名字级口径看不见这个缺失**（缺口一直是 17，没动）。

新增 `tools/bind_scope.py`：按**类型自己的源码块**检查绑定成员，答案完全不同 ——
**23 个已存在类型**在各自类型上缺成员（`LoginControl` 缺 `Cancel/OpenBrowser/SignIn/SignUp/UseCode`、
`UserView` 缺 `OpenUrl`、`CreateModel` 缺 17 个……）。

### 使用纪律

- 它是**筛查器，不是判决**：块提取靠"下一个声明"启发式，**基类/partial 里的成员会被误报**；
- 每条都要**手工复核一次**再动手（R342 抽查 `LoginControl`、`UserView` 两条，均为真）；
- 修完一条就在 `docs/VERDICT.md` 记一行，别让这 23 条变成新的"一句话包着的 backlog"。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('METHOD §10 added')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 342 轮：`IWebhook` 补齐六个成员 —— 顺带发现缺口口径的**盲点**

### 一、先按绑定表补

```
Cybersole.Webhook.IWebhook -> Enabled, Events, ExtraFields, Name, Type, Url
```

复刻件的 `IWebhook` **只有 `ExtraFields`**。已补齐六成员，`Webhook` 实现之；
`New Webhook` 表单里**本来就在收集、然后被丢掉**的两项（Platform 下拉、Events 复选）现在真正存下来了。

```
IWebhookContractTests   3 通过
完整套件                1505 通过 / 0 失败 / 2 跳过
```

### 二、可是缺口数字**没动**（还是 17）

这是本轮最重要的发现：名字级口径问的是"整个仓库里有没有这个名字"，
`Events` / `Type` 在别处早已存在（`TaskGroup` 等），所以 **`IWebhook` 缺成员这件事被口径吃掉了**。

### 三、换口径看一眼，答案完全不同

新写 `tools/bind_scope.py`：按**类型自己的源码块**检查成员。结果：

```
23 个"类型已存在但该类型上缺成员"
  LoginControl      Cancel, OpenBrowser, SignIn, SignUp, UseCode
  UserView          OpenUrl
  CreateModel       17 个（AccountGroup, Group, Input(s), IsEditing, MonitorDelay, …）
  BotTask           Products, Profile, Properties, ProxyGroup, Status, Task
  … 共 23 类
```

**抽查两条，全是真的**：`LoginControl` 只有构造器与 `Text(key)`，五个操作都没实现。

### 四、所以"缺口 17"这句话要改

准确说法应该是：

> **名字级缺口 17（成员名在整个仓库里都出现过）；类型级缺口 23 类（成员没长在它该在的类型上）。**

两个口径都对，但**后者才接近"功能 1:1"**。

### 五、这一轮的一句话

> 我用了三百多轮的"缺口 17"，原来只回答了"这个名字有没有出现过"。

> **指标一旦成为口号，就会失去分辨率 —— 换个口径，同一份代码立刻露出 23 个真缺口。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
