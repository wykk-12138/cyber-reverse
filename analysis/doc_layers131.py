import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 更正：指纹是**三层**，`Fingerprint.template.json` 属于 3DS 那层（第 131 轮）

R130 我把 `Fingerprint.template.json` 当成「浏览器指纹模板」。这一轮按资源全名查下去，**错了**。

### 资源全名

```
Cybersole.Core, Version=5.18.32.0, Culture=neutral, PublicKeyToken=null
  Cybersole.Helpers.Dlpa.Fingerprint.template.json
```

**命名空间是 `Dlpa`** —— 不是浏览器相关的命名空间。

### 它填的是一份 3-D Secure 设备画像

同一条字面量里的字段是支付方案的（EMVCo / 3DS2）口径：

```json
{"fingerprintAttempted":false,"fingerprintData":null,"challengeWindowSize":null,
 "threeDSCompInd":"Y","browserJavaEnabled":false,"browserJavascriptEnabled":true,
 "browserLanguage":"en-US","browserColorDepth":"24","browserScreenHeight":"1440",
 "browserScreenWidth":"5120","browserTZ":"-60","browserUserAgent":"…"}
```

注意 **`browserScreenWidth":"5120"`、`browserTZ":"-60"`** —— 值都是**字符串**，
而且 5120×1440 这种超宽屏正是「设备画像」要报的东西。

### 于是三层，不是一层

| 层 | 内容 | 谁在用 |
|---|---|---|
| **browser** | 8 字段（ColorDepth / DeviceMemory / HC / PixelRatio / Screen*） | 每个 Chrome profile（R130 已实现） |
| **payload** | `fingerprint-v1` 与 **`fingerprint-v1-sans-ua`** 两个变体 | 反爬脚本，按「UA 是否已在别处发送」二选一 |
| **dlpa** | 3DS 设备画像（`Fingerprint.template.json`） | **每一次支付** |

`fingerprint-v1-sans-ua` 这个名字本身就是一条结论：**同一个 payload 有「带 UA」和「不带 UA」两种发货方式**，
不是版本号，是调用方的选择。

### 对 R130 的影响

R130 的实现（`BrowserFingerprint`，每 profile 一套）仍然成立 —— 只是它属于**第一层**，
不是模板生成的。模板生成的第三层（3DS 画像）**还没实现**：支付时需要一份与浏览器层
**不矛盾**的画像（屏幕尺寸、色深、时区要和浏览器一致，否则同一笔支付自相矛盾）。

### 这一轮的一句话

> 「模板 → 指纹」这个理解很顺，顺到我根本没去读资源的全名。**读了一下全名，结论就变了。**
>
> **文件名和命名空间是零成本证据，而我总是先猜语义再去找证据。**
'''

if "## 更正：指纹是**三层**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("three-layer correction documented")
else:
    print("already present")
