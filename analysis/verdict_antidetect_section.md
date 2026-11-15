### 反检测参数生效了，但 Offspring 还是空白

上轮说「试给 Chromium 加反检测参数，改一行，便宜的实验」。改了三个：

```csharp
"--disable-blink-features=AutomationControlled",
"--disable-features=IsolateOrigins,site-per-process",
"--exclude-switches=enable-automation",
```

### 参数确实生效

探测脚本读的是浏览器自己报的值：

```
webdriver: false      ← 之前是 true
plugins:   5          ← 真实 Chrome 的数量
ua:        Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 …
```

**三个最常被检测的标记全部清掉了。**

### 但页面还是 11 个 div

```
{"url":"https://www.offspring.co.uk/",
 "title":"OFFSPRING",
 "anchors":0, "divs":11, "bodyLen":3298}
```

**和加参数之前一模一样。**

### 所以拦的不是 `navigator.webdriver`

这个实验排除了最常见的那个假设。剩下的可能：

| 假设 | 怎么验 |
|---|---|
| Akamai 要真实鼠标/键盘事件（`isTrusted`） | CDP `Input.dispatchMouseEvent` 可以产生可信事件 |
| 要特定 cookie（sensor 已通过的标记） | 需要先过一次挑战 |
| headless 的其他指纹 | 已经是 headed 模式了，排除 |
| 页面本身就是这样，内容靠 API 拉 | 但 `NetClient` 拿到 192 KB HTML，说明有内容 |

**第三种和第四种都被证据排除了**（headed 模式 + 192 KB HTML）。

**前两种需要更深的介入**，而那是 Playwright 或真人在环才能做的。

### 结论的强度变了

上一轮说「需要一个 Akamai 认的浏览器会话」。这一轮把「认」这个字**缩小了范围**：

> 不是「不要报 `webdriver`」，是「要真实事件序列或已通过的 sensor cookie」。

**这个区别决定了下一步该做什么**：不是继续调浏览器启动参数，而是要么注入可信事件，
要么复现 Akamai 的 sensor 挑战。前者 CDP 支持（`Input.dispatchMouseEvent` 带
`isTrusted: true`），后者是逆向工作。

### 三个参数的保留价值

即使对 Offspring 无效，这三个参数也应该留着：

- `--disable-blink-features=AutomationControlled` —— 去掉最显眼的自动化标记
- 对**其他**有轻量检测的站点有用（`goat` `scheels` 之类可能只看这一个）
- 没有副作用（headed 模式下本来就该关掉）

已写进 `ChromiumBridge` 的启动参数，注释里说明了它是为 Offspring 加的。

### 这一轮的净收获

**零个端点，但一个假设被排除了。**

从「需要 Akamai 认的会话」到「不是 webdriver 检测，是事件序列或 cookie」——
**问题的形状清楚了，虽然答案还没有**。

---
