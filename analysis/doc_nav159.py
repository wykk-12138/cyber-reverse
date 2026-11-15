import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 整份 `NAV` 取全：它是 **iOS 上的 Chrome**（第 159 轮）

上一轮只读了三行。把整条 `const NAV` 拉出来，长度是 16 个字段。

### 一、逐字（关键处）

```
"appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15
               (KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1",
"platform": "iPhone", "product": "Gecko", "productSub": "20030107",
"vendor": "Apple Computer, Inc.", "vendorSub": "",
"language": "nl-NL", "onLine": true, "pdfViewerEnabled": true
```

**`CriOS/156.0.8078.54`** —— 这是 **iOS 上的 Chrome**，但 iOS 只允许 WebKit，所以
`vendor` 仍是 `Apple Computer, Inc.`、`product` 仍是 `Gecko`。这台机器是**荷兰语（nl-NL）**。

### 二、`appVersion` 不是常量，是 UA 去掉 `Mozilla/`

```
userAgent   = "Mozilla/5.0 (iPhone; … Safari/604.1"
appVersion  = "5.0 (iPhone; … Safari/604.1"
```

一模一样，只差前缀。所以这一版改成**派生**而不是写死 —— 两个相邻属性如果说两套话，就是自相矛盾。

### 三、还有两份清单：`NAV_ORDER` 与 `NAV_KEYS`

```
NAV_ORDER = 49 项，按 for-in 走过的顺序
NAV_KEYS  = 51 项，含 __defineGetter__ / hasOwnProperty 等
```

**枚举顺序本身就是指纹** —— 一个 `for in navigator` 的检测器读的是顺序，不是集合。
已作为 `MobileNavigator.NavOrder` 记录（顺序原样保留）。

### 四、顺带发现：`CRED_SHIM`

```
const CRED_SHIM = [{"name": "get", "length": 1, "src": "function(e){if(!e?.publicKey)…"}]
```

—— 连 `navigator.credentials.get` 的 shim 都带着**长度**和一段**压缩后的源码**，
因为 `Function.prototype.toString` 会读源码。**shim 的伪装不止在行为上，还在它的文本上。**
这条留给后续轮次。

### 五、自己踩的坑：测量时机

`TheZoomRatioIsExactlyOne` 突然报 `Cannot read properties of null`。
诊断表达式一改就看清了：

```
ratio inputs = ["no-documentElement","loading"]
```

**导航在文档解析完成之前就返回了。** 之前在别的轮次恰好赶上了，这次没赶上 ——
所以测量前必须等 `document.readyState === 'complete'`。已加进测试工装。

### 六、这一轮的一句话

> 上一轮我以为 `NAV` 是三行。它其实是十六个字段 + 两份顺序清单 + 一个 shim。
>
> **「读完了」的感觉，通常只是「读到了我以为重要的那部分」。**
'''

if "## 整份 `NAV` 取全" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("NAV documented")
else:
    print("already present")
