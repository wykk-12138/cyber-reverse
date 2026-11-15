### 从「读源码」转到「问浏览器」：一次真实探测推翻了三个猜测

R136–R138 三轮都是读 `hcaptcha-spoof.js` 的注释，推断 replica 缺什么。这一轮换了方向：
**启动真的 Chrome，把检测方会问的问题都问一遍。**

### 探测结果

```
isSecureContext                  false
UA                               Mozilla/5.0 (Windows NT 10.0; Win64; x64)
                                 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36
uaData.fullVersion               absent
uaData.brands                    absent
webdriver                        undefined
ontouchstart in window           False
ontouchstart shape               no descriptor
getVoices length                 6
getVoices first                  Microsoft David - English (United States)
plugins length                   3
hardwareConcurrency              8
document own props (first 8)     location
document has featurePolicy       present
document has browsingTopics      absent
navigator own props count        36
navigator has userAgentData      absent
webkit in window                 False
chrome in window                 True
iframe navigator.webdriver       webdriver=undefined voices=6
```

### 三个猜测被推翻

**一、「`userAgentData` 不一致」——在 `data:` URL 上根本不存在**

R138 花了一整轮修 UA 和 `userAgentData` 的矛盾。**但这个会话里 `userAgentData` 是 `absent`。**

原因不是修错了，是**探测页面不对**：`navigator.userAgentData` **只在安全上下文里存在**，
而 `data:text/html,…` 不是安全上下文。

**`isSecureContext: false`** 解释了这一整行。

**R138 的修复仍然是对的**（源码里两条路径现在都从 `ChromiumBridgeVersion()` 取版本），
**但它在这个页面上无法被观测。**

> **一个测试看不到的东西，不等于不存在；先确认测试站在哪。**

**二、「`ontouchstart` 缺失是缺口」——不是**

原版的 `HANDLERS` 表（`onabort` / `onafterprint` / `ontouchstart` … 一大串）是为了
iOS 准备的，注释写得很清楚：

```
aK_ = ('ontouchstart' in window);  lK = uS && aK_ && <ua not Safari-shaped>;  QW = nW || lK
With aK_ false the gate opens and we spawn a worker a real iPhone never spawns.
```

**这台机器的桌面 Chrome：`ontouchstart in window` = `False`，而且连 descriptor 都没有。**

**这是正确答案。** 一台没有触摸屏的 Windows 桌面，本来就不该有 `ontouchstart`。
如果 replica 为了「看起来完整」把这一串 handler 都装上去，**反而会被抓**——
一个声称没有触摸屏的设备却有 `ontouchstart`，那是自相矛盾。

**三、「`document` 的 own property 太少」——不少**

`Object.getOwnPropertyNames(document)` 只返回 `location`（前 8 个里就 1 个）。

**这是 Chrome 的正常行为**：`document` 的绝大部分成员在 `Document.prototype` 上，
不在实例上。原版 `DOCUMENT_PRUNE` 操作的就是 `realm.Document.prototype`。

### 两条真的对上了

**`getVoices()` = 6** —— R137 加的补丁生效了。
`getVoices first: Microsoft David - English (United States)` 就是补丁表的第一项。

**`iframe: webdriver=undefined voices=6`** —— R136 的 realm 重放和 R137 的 voice 补丁
**都传到了子 frame**。这是唯一一条能证明那两轮真的起作用的证据。

**如果只看源码，`PATCHED.add(win)` 和 `contentWindow` getter 都在；**
**只有真的建一个 iframe 去读，才知道它们连起来了。**

### 一个诊断工具，不是一条测试

这个探测被标成 `Speed=Slow`，只在 `-Full` 或显式过滤时跑——**它会启动浏览器，两分钟。**

它的价值不在断言，在输出。三条断言只覆盖了已经修好的东西：

```csharp
Assert.False(string.IsNullOrEmpty(uaToken));
Assert.DoesNotContain("webdriver=true", child);
Assert.DoesNotContain("voices=0", child);
```

**真正的产出是那张 19 行的表。** 下一轮再怀疑什么，先跑它。

### 顺带记一件事：全量测试的偶发失败

`dotnet test`（含 Slow）第一次跑出 **9 个失败 / 886 通过**，第二次**895 通过 / 0 失败**。

差的那 9 个在 `CheckoutFailureModeTests` / `ImapProviderTests` 那一类——
它们本来就在跑真实网络和端口。**这个探测同时启动了一个 Chrome 实例，抢端口。**

**记下来：`-Full` 模式下 Chrome 探测和网络测试会互扰。** 不是缺陷，是资源竞争。

### 验证

```
dotnet test --filter "Speed!=Slow"   643 通过 / 0 失败 / 2 跳过
dotnet test（含 Slow）               895 通过 / 0 失败 / 2 跳过
live contracts                      PASS
store modules                       PASS 61 registered
```

---
