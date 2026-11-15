### `fanatics` 定性：Akamai 直接 403，连页面都不给

带止损条件跑了一次抓包（「一分钟内看不出是什么拦的就停」）。

### 结果

```
403  GET  https://www.fanatics.com/
200  GET  https://www.fanatics.com/favicon.ico
200  GET  https://www.fanatics.com/_es_/fo/ping/0.a4f7d517.1794315806.819ca3e

hosts seen: 3 × www.fanatics.com
```

**`/_es_/fo/ping/` 是 Akamai Bot Manager 的 sensor beacon。**

### 和 Offspring 的区别

| | `offspring` | `fanatics` |
|---|---|---|
| 首页响应 | **200 + 192 KB HTML** | **403，无内容** |
| 浏览器 DOM | 11 div（reCAPTCHA 挡住） | 无 DOM（页面没加载） |
| 门禁类型 | **reCAPTCHA**（`recaptcha__z…`） | **Akamai Bot Manager 直接拒** |
| 能不能过 | 打码服务可以 | 需要 Akamai sensor 会话 |

**Fanatics 比 Offspring 更硬**：Offspring 至少给了 HTML（所以 R64 能验证 Hybris 的
`/view/` controller），Fanatics 连 HTML 都不给。

### 四个站点的最终分类

| 模块 | 障碍 | 需要什么 | 代码能解决吗 |
|---|---|---|---|
| `offspring` | reCAPTCHA | 打码服务（运行时配置） | ❌ 属于用户配置 |
| `fanatics` | Akamai Bot Manager | Akamai sensor 会话 | ⚠️ 可逆向，工程量大 |
| `scheels` | Kasada | Kasada sensor 会话 | ⚠️ 同上 |
| `bstn` | 商品卡是 CSS 背景图 | 下一层 DOM 探测 | ✅ 可以，但已知多两道未知 |

**前三个是「过风控」，第四个是「还没探明结构」。**

### `fanatics` 这个模块现在的状态

`FanaticsFlow` 实现完整（`FindProduct` / `FindVariant` / `AddToCart` / `SubmitOrder` 都有），
只是**打不到站点**。

它的失败信息会是什么？`GetHomeAsync` 里应该有 `403` 分支——查一下确认它是诚实的。

（如果它把 403 当成通用失败，那是个可以小修的点：403 应该说明「被风控拦」而不是「HTTP 403」。）

### 为什么这轮只做了一件事

因为**它确实是只需要一分钟的事**。止损条件在跑之前就定了，跑完就有结论。

对比 R53–R56 那四轮 BSTN——没有止损条件，每轮都是「换一种方法试试」。

**「先定放弃条件」这个方法本身，比任何一次探测都值钱。**

---
