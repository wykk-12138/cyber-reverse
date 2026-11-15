import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 两个一直缺的 prune：window 和 document（第 184 轮）

replica 一直有 `navigator` 的 prune，**从来没有 window 和 document 的**。原版两处都有。

### 一、`GLOBAL_PRUNE`：`chrome` 是被删掉的

```js
const KEEP = new Set(['hsw','Raven','_sharedLibs','webkit','__wdata','__hcLoggerInstalled',
  '__hcWorkerProbeInstalled','__hcWorker','__hcCollector','__hcLogCalls','__hcSweepDelay']);
GLOBAL_PRUNE = (realm) => {
  nativeOwnNames(realm).forEach((key) => {
    if (!DEVICE_GLOBALS.has(key) && !KEEP.has(key)) { try { delete realm[key]; } catch (e) { } }
  });
};
```

`DEVICE_GLOBALS` 就是上一轮那 **1062** 个名字的 Set。凡是设备没有、又不在 KEEP 里的，删。

**为什么它是函数而不是一次性循环**：

> A child realm arrives with a fresh global carrying the full Blink surface again. Deleting only in this realm left
> `'chrome' in window` false at the top and TRUE inside an iframe — **and the challenge runs in an iframe**, so the
> frame that matters was answering honestly.

### 二、`DOCUMENT_PRUNE`：第一个请求就输了

```
['featurePolicy','hasPrivateToken','hasRedemptionRecord','hasTrustToken',
 'browsingTopics','requestStorageAccessFor','prerendering','startViewTransition']
```

> hCaptcha's checksiteconfig — the FIRST request of the whole flow, in plaintext, before a single sensor byte —
> carries `spst`, computed as `!(document.hasPrivateToken === undefined || …) && featurePolicy.allowsFeature(…)`.
> Private State Tokens and featurePolicy are Blink-only; WebKit has never shipped either, so a real Chrome-on-iOS can
> only ever answer 0. **We answered 1.** Verified against a device capture on the SAME sitekey AND the same api.js
> build: device spst=0, bot spst=1 — the only apples-to-apples comparison in the whole artifact set, and we were
> losing it on request one.

### 三、实测

```
probe = [false,"undefined",false,false,true,"object"]
          ↑无 chrome  ↑typeof 是 undefined  ↑无 featurePolicy  ↑无 hasPrivateToken  ↑mask 还在
child = [false,false]
          ↑iframe 里也没有 chrome  ↑也没有 featurePolicy
```

### 四、这一轮的一句话

> 我们花了很多轮让 `navigator.platform` 看起来对，而 `'chrome' in window` 一直是 `true` ——
> **一行就能问倒的，往往不是最复杂的那一行。**
>
> **最响的谎话，通常是最短的那句。**
'''

if "## 两个一直缺的 prune" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("documented")
else:
    print("already present")
