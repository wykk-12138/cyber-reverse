### 一个从没红过的测试，不能证明它测到了东西

R136–R138 写了五个守护测试。这一轮把它们各自对着的缺陷**原样改回去**，
看测试是否真的会红。

### 结果：五个变异，一个伪装成绿色的

| 变异 | 结果 |
|---|---|
| R136 `contentWindow` 重放路线改成 `null` | **guard fired** |
| R136 `createElement` 重放路线改成 `null` | **第一轮：GREEN（装饰性）** → 加强后 guard fired |
| R136 把 `N.webdriver` 改回裸 `navigator.webdriver` | **guard fired** |
| R137 `getVoices()` 改回 `return []` | **guard fired** |
| R138 `fullVersion` 改回硬编码 `"131.0.0.0"` | **guard fired** |

### 那个装饰性的断言长什么样

```csharp
Assert.Contains("Document.prototype.createElement", script);
```

`Document.prototype.createElement` 在那个脚本里**出现两次**：

```js
const createElement = Document.prototype.createElement;      // 保存原函数
Document.prototype.createElement = function (tag) { … };     // 替换
```

我把第一行改成 `const createElement = null;`，**第二行还在**，字符串照旧命中，
断言通过，**而钩子已经死了**——`createElement.apply` 会在调用时抛 `TypeError`，
被外层的 `try { } catch (e) { }` 吞掉，**整个 `createElement` 路线静默失效**。

### 修：钉住做事的那个语句，而不是它包含的词

```csharp
Assert.Contains("const createElement = Document.prototype.createElement;", script);
Assert.Contains("Document.prototype.createElement = function (tag)", script);
Assert.Contains("const descriptor = Object.getOwnPropertyDescriptor(proto, 'contentWindow');", script);
Assert.Contains("Object.defineProperty(proto, 'contentWindow', {", script);
Assert.Contains("el.addEventListener('load', () => replay(el.contentWindow));", script);
```

**五条，每条对应一个必须存在的语句。** 少任何一条，那条路线就不完整。

### 这暴露了一类问题，不只是这一个测试

`RealmReplayTests` 里其他几条当时也是这个形状：

```csharp
Assert.Contains("new WeakSet()", script);
Assert.Contains("Document.prototype.createElement", script);
Assert.Contains("HTMLIFrameElement.prototype", script);
```

**「某个词出现过」是最弱的断言形式**——它只排除「整个功能被删掉」，
**不排除「功能被改坏了」**。

而 R136 那一轮，我正是因为「源码里有这些词」而宣布修好了。

### 五个变异都红了之后

```
guard fired   round 136 — the contentWindow replay route
guard fired   round 136 — the createElement replay route
guard fired   round 136 — replay a fresh realm through a bare global
guard fired   round 137 — speechSynthesis voices
guard fired   round 138 — one version reading
restored tree: GREEN
```

**每个变异跑完都恢复原文件**（`try/finally`），最后再跑一次全量确认树是绿的。

### 固化成工具

`tools/mutation-check.py`（4,859 字节），和 `verify.ps1` 放在一起。

结构是一个表：

```python
MUTATIONS = [
    {
        "name": "round 137 — speechSynthesis voices",
        "file": BRIDGE,
        "find": "                value: function getVoices() { return voices.slice(); },",
        "replace": "                value: function getVoices() { return []; },",
        "test": "FullyQualifiedName~RealmReplayTests",
        "guard": "SpeechSynthesisReturnsAVoiceList",
    },
    …
]
```

**加一条变异就是加一个字典。** 判据是二值的：

```python
if code == 0:
    verdict = "GUARD IS DECORATIVE — tests stayed green"
else:
    verdict = "guard fired"
```

**「测试没红」不是通过，是失败。**

### 一个已知的边界

**这个工具只能测「源码里的形状」**。R136 的 `contentWindow` 重放路线有两个测试覆盖：
源码形状（`BothIframeRoutesAreHooked`）和真实行为（`LiveBrowserProbeTests` 里那个
建 iframe 读 `navigator.webdriver` 的探测）。

**变异只跑源码形状那一层。** 真实行为那层要启动浏览器，两分钟一次，
不适合放进变异循环。

**所以「guard fired」的含义是：源码形状的守护有效。**
真机行为是否有效，只有 `-Full` 会回答。

### 验证

```
五个变异          全部 guard fired
恢复后全量        643 通过 / 0 失败 / 2 跳过
live contracts    PASS
store modules     PASS 61 registered
tools/mutation-check.py  4,859 字节
```

---
