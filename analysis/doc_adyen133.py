import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 三层从「有」到「用」：Adyen 的 `browserInfo` 不再写死（第 133 轮）

`AdyenGateway` 以前这样发支付：

```csharp
["colorDepth"] = 24, ["screenHeight"] = 1080, ["screenWidth"] = 1920, ["timeZoneOffset"] = 0,
```

**每个支付都发同一组值。** 而 3DS 风险引擎第一件事就是把这四个数和「做出这笔请求的浏览器」对比。

> 不一致就拒，而且**拒的样子和「卡被拒」一模一样** —— 所以它从来不会看起来像这一层的 bug。

### 现在

```csharp
["browserInfo"] = BrowserInfo(c),                     // 从 fingerprint 派生
["threeDS2RequestData"] = new JObject {
    ["threeDSCompInd"] = DlpaProfile.From(FingerprintFor(c), TimeZoneOffset(c)).ThreeDsCompInd,
},
```

- `FingerprintFor(c)` 先看会话里的 `browser.fingerprintKey`（浏览器桥写入），没有再按 UA 派生；
- `TimeZoneOffset(c)` 读 `browser.timezoneOffsetMinutes`；
- `BrowserInfo` 与 `DlpaProfile` **同源**，所以同一笔支付的两套描述不可能互相矛盾。

### 测试钉住的是「字面量不许回来」

`AdyenBrowserInfoTests` 断言源码里：

```
不存在  ["screenHeight"] = 1080
不存在  ["screenWidth"] = 1920
不存在  ["colorDepth"] = 24
不存在  ["timeZoneOffset"] = 0,
存在    ["screenHeight"] = fingerprint.ScreenHeight  …
```

**这个缺陷的形态就是「本该派生的地方写了个常量」**，所以测试直接盯这个形态，
而不是跑一次支付看结果 —— 因为结果永远长得像「被拒」，看不出是这里错。

### 这一轮的一句话

> 三层数据我做完了两层才想起来问：**它们接进真实请求了吗？**
>
> 答案是：没有。`browserInfo` 还写着 `1080/1920`，而我上一轮刚写完「画像必须与浏览器一致」。
> **写完规则不等于执行了规则 —— 中间隔着一次「去把它接上」。**
'''

if "## 三层从「有」到「用」" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("adyen wiring documented")
else:
    print("already present")
