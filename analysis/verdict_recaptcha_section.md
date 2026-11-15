### 找到根因：Offspring 用 reCAPTCHA 当门禁

上一轮排除了 `navigator.webdriver`，留下的两个假设是「要真实事件」和「要 sensor cookie」。
这一轮加了 CDP 鼠标点击（产生 `isTrusted: true`），然后去看 DOM 的真实状态。

### 那个探测脚本读到了答案

```json
{"url": "https://www.offspring.co.uk/",
 "divs": 11, "bodyLen": 3298, "anchors": 0,
 "scripts": 4,
 "firstScriptSrc": "https://www.gstatic.com/recaptcha/releases/…/recaptcha__z…"}
```

**整个页面只有 4 个 `<script>`，第一个是 reCAPTCHA。**

### 所以「DOM 只有 11 个 div」有了解释

不是 JS 没跑，是 **JS 跑了但被 reCAPTCHA 挡住**：

| 层 | 内容 |
|---|---|
| `NetClient` GET | 192 KB 完整 HTML（服务器照发） |
| 浏览器 DOM | 11 个 div（reCAPTCHA 脚本挂上后，页面主体不再渲染） |
| `<script>` | 4 个，第一个是 `recaptcha__z…` |

**这也解释了 R64 为什么能验证 Hybris**：`/view/resources/getUserInfo` 和
`/view/component/basket/minibasketAjax` 是 **API controller**，不过 reCAPTCHA 门禁——
所以它们返回 200 JSON，而页面本体渲染不出来。

### 三个假设，排除两个

| 假设 | 结果 |
|---|---|
| `navigator.webdriver` 检测 | ❌ 加了参数变 false，页面没变 |
| 要 `isTrusted: true` 的鼠标事件 | ❌ CDP 点击后 DOM 还是 11 div |
| **要过 reCAPTCHA** | ✅ **脚本 URL 直接证明了** |

### 这意味着什么

**`offspring` 的加购端点拿不到，需要的不是更好的探针，是过 reCAPTCHA。**

而 reCAPTCHA 过不去不是技术问题——**Cybersole 本身也不"过" reCAPTCHA，它调用打码服务**。
`CaptchaSolverService` 就是干这个的，而我们复刻了它。

**所以正确的判断是**：`HybrisFlow.AddToCartAsync` 现在的失败信息是对的——

```
offspring: cart-add controller not found — /cart/add, /view/cart/add,
/view/component/cart/add and /view/component/basket/add all return 404 while the
control minibasketAjax returns 200, so the route is customised; needs a click-through
capture of the add-to-basket button
```

**要补上「click-through capture」，前置条件是过 reCAPTCHA**，而那属于运行时的事
（用户配了打码服务才有），不是实现的事。

### 工具链的净增

`NetworkRecorder` 新增三个方法：

```csharp
MouseMoveAsync(x, y)
MouseClickAsync(x, y)        // mouseMoved → mousePressed → 60ms → mouseReleased
MouseClickAsync(selector)    // 找到元素中心，走上面的路径
```

`NetworkCapture` 新增两个开关：

```
--mouse=<css>       按元素点
--mouse-xy=x,y      按坐标点
```

**CDP `Input.dispatchMouseEvent` 产生的事件带 `isTrusted: true`**，这是 `el.click()`
做不到的。对 Offspring 无效（因为拦住它的是 reCAPTCHA），但对只查事件可信度的站点可能有用。

### 这一轮真正的收获

**一个站点彻底定性了。**

从「需要 Akamai 认的会话」→「不是 webdriver」→「不是事件可信度」→ **「是 reCAPTCHA」**。

三轮排查，每一轮排掉一个假设，最后落到一个**不在代码范围内**的答案。

**这比"还没搞明白"有用得多**——现在知道继续投入是浪费。

---
