### 乱码：54 处，17 个文件，全在注释里

查 `Custom Stores` 的 `AddPreset` 时，顺手看到 `Registry.cs` 里一行注释：

```csharp
/// settings.customStores 鈥?each user-defined shop becomes a Shopify alias
```

**`鈥?` 应该是 `—`。**

`AddPreset` 本身是真的（URL 校验 → 规范化 → 加进列表 → 保存 → 刷新），
而且那句「resolves as a Shopify alias」也对——`RegisterCustom` 确实把它们注册成 `ShopifyFlow`：

```csharp
registry.Register(new FlowStoreModule(new ShopifyFlow(id, name, new[] { host })));
```

**所以功能没错，是注释脏了。** 但脏一处就要查全库。

### 扫出来 54 处，三个变体

```
鈥?  x47   （em dash）
鈫?  x6    （right arrow）
閳?  x1    （colon 或 dash）
```

**分布在 17 个文件**：`TaskCombinationBuilder` / `Drivers` / `GoogleOAuthFlow` /
`FootsitesFlow` / `ShopifyFlow` / `Registry` / `AdyenGateway` / `ChromiumBridge` /
`ScriptRuntime` / `ProfileViews` / `MailAndCaptchaTests` …

**成因**：某个时刻有文件被以 GBK 解码后又存成 UTF-8。**之后每一次编辑都保留了这份损坏。**

### 修

```python
REPAIRS = [
    ("\u9225?", "\u2014 "),   # 鈥? -> em dash + space
    ("\u922b?", "\u2192 "),   # 鈫? -> right arrow + space
    ("\u95b3?", "\u2014 "),   # 閳? -> em dash + space
]
```

54 处全修，重扫 0。

### 修的过程中造了一个新错

`ShopifyFlow.cs` 原来是这样（损坏版）：

```
/// Walked in the order the binary uses: product JSON 鈫?cart/add 鈫?cart.js 鈫?/// checkout token → ...
```

那个 `鈫?///` 是 **「箭头 + 换行 + 注释符」** —— 原文应该是：

```
/// ... cart.js →
/// checkout token → ...
```

**我的替换加了空格，变成 `→ /// checkout`** —— 箭头后面跟着注释符，读起来像句子中间冒出半行注释。

**修第二遍**：把它拆成两行。

**然后加了一条测试专门盯这个形状**：

```csharp
var glued = new Regex(@"[\u2192\u2014]\s*///");
```

### 测试自己也有乱码

第一次跑 `SourceEncodingTests` 报：

```
tests/Cybersole.Tests/SourceEncodingTests.cs:10  鈥?
tests/Cybersole.Tests/SourceEncodingTests.cs:10  鈫?
tests/Cybersole.Tests/SourceEncodingTests.cs:11  閳?
tests/Cybersole.Tests/SourceEncodingTests.cs:88  /// One occurrence produced "cart.js → /// checkout".
```

**因为我在注释里把这三个序列当例子写出来了。**

改成用文字描述（「an em dash, a right arrow and a colon, each written as two CJK-ish bytes
followed by a question mark」），不再写出字面。

> **一个检查乱码的测试，自己不能包含乱码。**

### 两条测试

| 测试 | 挡什么 |
|---|---|
| `NoSourceFileContainsMojibake` | 任何 CJK 字符紧跟 `?` 或 `\ufffd` |
| `NoCommentMarkerIsGluedToAnArrowOrDash` | `→ ///` 或 `— ///` |

```
mojibake hits: 0
glued comment markers: 0
```

### 为什么这件事值得做

**54 处全在注释里，没有一处影响行为。**

但看到一个文件里注释是乱码，读者会想：**「代码本身有没有也被这样损坏过？」**
**这个问题没法靠看注释回答。**

修完之后，`git diff` 里那 17 个文件是干净的——**它们的历史里不再有「这段曾经坏过」的痕迹**。

### 验证

```
dotnet test      551 通过 / 0 失败 / 2 跳过   (+2 SourceEncodingTests)
live contracts   PASS
store modules    PASS 61 registered
build errors     0
```

---
