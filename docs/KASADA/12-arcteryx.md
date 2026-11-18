# 12 · Arcteryx：无浏览器取 ct 的方案在这里**不适用**（实测）

上一轮交付的 `KasadaHttpHandshake`（`/mfc` → `/fp` → `ips.js`，见 `11-jint-runtime.md` §7）
在 **Nike 上有效**。这份记录是它在 **arcteryx.com** 上的实测结果：

> **不适用。** 拿到的 ct 是中间值，业务端点一律 429。

交接包 `kasada_arcteryx/README.md` 的判断是对的，下面是独立复现的证据。

---

## 1. 逐跳对照

同一套请求头（Chrome 143 的 UA + `sec-ch-ua*` + `referer: /us/en/checkout`）：

| 跳 | Nike | Arcteryx |
|---|---|---|
| `GET {dir}/fp?x-kpsdk-v=…` | 200，回 `x-kpsdk-ct` | 200，回 `x-kpsdk-ct` **但这是中间值** |
| `GET {dir}/ips.js?KP_UIDz=…` | 200，**回新的 `x-kpsdk-ct`** | 200（462,465 字节），**响应头里没有 ct** |
| `POST {dir}/tl` 空 body | 200 | 200，**正文 0 字节**，带 `x-kpsdk-cr: true` |
| `GET /api/cart.get` | （Nike 无此门） | **429** |

**关键差异在第 2 跳**：Nike 的 `ips.js` 会再签发一个 token，Arc 的不回。
所以纯 HTTP 走完三跳，手里只有一个来自 `/fp` 的中间 token。

## 2. `cart.get` 六组对照（全部 429）

| 打什么 | 结果 |
|---|---|
| 无 ct（负对照） | **429** |
| 假 ct `FORGED0000000000000000` | **429** |
| `/fp` 的中间 ct + 真 h | **429** |
| `/tl`（空 body）回的新 ct + h | **429** |
| `/tl` 回的新 ct + h + 它给的 `x-kpsdk-st` | **429** |

**五组全 429。** 连 `/tl` 回来的 ct 也不管用 —— 因为那次 `/tl` 是**空 body**，
按交接包 §1 的判据表，正文不是 15 字节 `{"reload":true}` 就等于"未解出"。

## 3. 独立复现了交接包的两个关键断言

这两条是这份记录里最有价值的部分 —— **文档说的是真的，不是拍脑袋**：

**（1）`/mfc` 的 `x-kpsdk-h` 与文档常量一字不差**

```
GET {dir}/mfc   x-kpsdk-h: 01   ->   01LAYcQHBsrRxyq9ja+CNVxPZlQ9g=
```

交接包 §2 写的就是 `01LAYcQHBsrRxyq9ja+CNVxPZlQ9g=`。**说明请求形态对、站点部署没变。**

**（2）`/tl` 空 body 就是"未解出"的形态**

```
POST {dir}/tl   body=0 bytes  ->  200，正文 0 字节
                                  x-kpsdk-cr: true
                                  x-kpsdk-r: 1-AQ
                                  x-kpsdk-st: 1795015475777
```

对照交接包 §1："HTTP 200 但**空正文**（常同时带 `x-kpsdk-cr: true`）" —— **完全吻合**。

**这也说明 `x-kpsdk-cr: true` 不是拒绝标记**（文档 §7 陷阱 2 说的对）：
它在我们明确失败的那次也出现了。

## 4. 顺带纠正 11 号文档里的一个说法

`11-jint-runtime.md` §8.1 写"`x-kpsdk-im` 是客户端算的，服务端不发"——
**那只对 Nike 成立。**

**Arc 的 `/fp` 正文里直接带了 `im`：**

```html
<script src="…/ips.js?KP_UIDz=…&x-kpsdk-v=j-1.2.904&x-kpsdk-im=AAJeOv-4jdPdhrKq_9Dt7TrgcdSYc3Fp_U5I1y16yMktu8VCgbcgyHiiby4KhweMYs-Nhr_96l_L39T-3IPMJb1k5KM…">
```

**所以 `im` 的来源随站点而异**，不能一概而论。

## 5. 为什么 Arc 过不去

交接包 §2 说得很清楚，我的实测与之一致：

> 业务必须用 **`/tl` 响应头**的 ct；`/fp` 的、HS payload 里的中间 CT 都不行。

而 `/tl` 要求 `content-type: application/octet-stream` + **数 KB 到数十 KB 的真实加密体**
（文档记的是 25,618 字节）—— 那份密文只能由脚本自己算出来。

**⇒ 纯 HTTP 造不出那份密文，这条路上没有捷径。**

这也和 Nike 不同：Nike 的 `/fp` 就直接给可用 token（虽然我们验证过 Nike 上没有需要它的门）。

## 6. 结论

| 问题 | 答案 |
|---|---|
| `KasadaHttpHandshake` 能用在 Arcteryx 吗 | **不能**，五组对照全 429 |
| 差在哪一步 | `/tl` 要真加密体，而密文只能由脚本算 |
| 交接包的判断对吗 | **对**，两个关键断言我都独立复现了 |
| 纯 JS 引擎（Jint/Node）能过吗 | 交接包说不能（`/tl` 空正文）；本会话没有对 Arc 重做这个实验 |

**要在 Arc 上拿可用 ct，只能跑 payload 或真浏览器** —— 和交接包 §6 那句结论一致：
"local 在 Arc 上等于真浏览器执行脚本、本地签名 CD"。

## 7. 未验证 / 边界

- **没有对 Arc 跑过 payload**（Jint 或 Node）。交接包说纯引擎过不了，我没在这个会话里重做。
- **没有验证 `catalog.*` 之类的宽松端点**：我试的 `catalog.getProductList` 是 404（端点名猜错），
  所以"中间 ct 能过宽松端点"这条只在交接包里有，我没复现。
- **没有拿到任何成功的 `/tl` 回合**，所以 CD 相关的结论全部来自交接包文档，不是实测。
- 只测了 US 站点，没测 CA。
