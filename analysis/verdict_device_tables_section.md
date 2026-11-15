### `Fingerprint.template.json` 是个空壳，真数据在 spoof 脚本里

R134 之后 `Cybersole.Core` 的 22 个资源提了 18 个，剩下最有价值的是
`Cybersole.Helpers.Dlpa.Fingerprint.template.json`。这一轮找它，**没找到——但找到了它该有的东西**。

### 为什么找不到

镜像里 `Dlpa` 只在两个地方出现：

```
0x32293fd   编译后的符号表（二进制元数据，不是 JSON）
0x3fa2f85   资源清单条目
```

按指纹键簇搜（`"userAgent"` / `"screen"` / `"canvas"` / `"webgl"` / `"timezone"` …），
最大的簇在 `0x3d0f7a3..0x3d14d37` —— **那是 `hcaptcha-spoof.js` 里面**。

**结论**：那个资源被 NativeAOT 裁剪了，或者本来就是个空文件。**模板名字存在，数据不在那里。**

### 真数据在 spoof 脚本的 29 个设备表里

`hcaptcha-spoof.js` 有 **29 个 `const` 设备表，131 个不同的键**：

| 表 | 行数 | 内容 |
|---|---|---|
| `NAV` | 115 | navigator 20 键 |
| `NAV_ORDER` | 113 | **属性枚举顺序** |
| `CRED_SHIM` | 112 | Credential Management 垫片（含伪装的源码） |
| `WINDOW_ALL` | 77 | window 全局列表 |
| `WINDOW_ENUM` | 76 | 可枚举的 window 键 |
| `CSS_DECL` | 75 | CSSStyleDeclaration 属性 |
| `CSS_PROPS` | 166 | 全部 CSS 属性名 |
| `GL_PARAMS` | 48 | WebGL 参数（webgl + webgl2） |
| `GL_META` | 47 | WebGL 扩展 + 元数据 |
| `VOICES` | 43 | 语音合成列表 |
| `QUERIES` | 41 | matchMedia 结果 |
| `MESSAGES` | 22 | 4 个错误消息模板（`null is not an object (evaluating 'null.x')`） |
| `HANDLERS` | 21 | `onabort` / `onafterprint` … 事件处理器 |
| `FONTS` | 19 | 字体度量 |
| `CANVAS` | 18 | canvas 的 base64 PNG |
| `GEOMETRY` | 18 | 设备宽高 |
| `BLINK_2X2` | 18 | 2×2 像素的 RGBA（Blink 渲染） |
| `DEVICE_2X2` | 17 | 2×2 像素的 RGBA（设备渲染） |
| `MEDIA` | 15 | codec 支持 |
| `GLOBAL_KINDS` | 15 | **59 个全局的类型标记** |
| `SCREEN` | 14 | 屏幕尺寸 |
| `SCREEN_ORDER` | 13 | 屏幕属性枚举顺序 |
| `ORDER` | 13 | 对象 `toString` 标签的匹配表 |
| `INTL` | 8 | `locale: "nl-NL"` |
| `PROGRAMS` | 5 | `build 52621c39 "96x48|0#fillRect(0,0,96,48)strokeText(…`
| `KNOWN` / `INTL_NAMES` / `FONTS_LOOSE` / `PATCHES` | 小 | 索引表 |

### 抓取设备的身份

```
NAV.userAgent     Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X)
                  AppleWebKit/605.1.15 (KHTML, like Gecko)
                  CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1
NAV.platform      iPhone
NAV.hardwareConcurrency  4
NAV.maxTouchPoints       5
SCREEN            402 × 874（iPhone 15/16 的逻辑分辨率）
GEOMETRY          device-width 402, device-height 874, height 684
INTL.locale       nl-NL
VOICES[0]         com.apple.voice.super-compact.nl-BE.Ellen
```

**一台荷兰语 iPhone 上的 iOS Chrome。** 和 R134 恢复的注释对得上：

```
// session-20261029-102720 (iOS 27.0.1 / CriOS 156) and transplanted
```

### 每张表都在防一种具体的检测

**不是「补全 navigator」，是逐条对着检测点做的**：

| 检测点 | 对应表 |
|---|---|
| `navigator` 读值 | `NAV` |
| **属性枚举顺序**（`Object.keys` 有顺序） | `NAV_ORDER` / `SCREEN_ORDER` / `ORDER` |
| `window` 上有哪些全局 | `WINDOW_ALL` / `WINDOW_ENUM` / `GLOBAL_KINDS` |
| **`Function.prototype.toString` 读出源码** | `CRED_SHIM` 的 `src` 字段 |
| `matchMedia` 查询结果 | `QUERIES` |
| WebGL 参数和扩展 | `GL_PARAMS` / `GL_META` |
| canvas 像素哈希 | `CANVAS` |
| **同一像素在 Blink 和 WebKit 下不同** | `BLINK_2X2` vs `DEVICE_2X2` |
| 字体度量（哪些字体装了） | `FONTS` |
| `Intl` 的 locale / 时区 | `INTL` |
| 语音合成列表 | `VOICES` |
| codec 支持 | `MEDIA` |

**`BLINK_2X2` 和 `DEVICE_2X2` 这一对最能说明问题**：
同一段 canvas 代码，Chrome 的 Blink 和 Safari 的 WebKit 渲染出**不同的 2×2 像素值**。
**要伪造 iOS Chrome，必须用 Blink 的值；用设备的值就露馅。**

**`NAV_ORDER` 是第二能说明问题的**：它伪造的不是值，是**枚举顺序**——
`Object.keys(navigator)` 的顺序在真实浏览器里是固定的，伪造一个对象时如果顺序不对，一样能被看出来。

### 九条测试

| 测试 | 断言 |
|---|---|
| `AllDeviceTablesArePresent` | **29/29** |
| `NavigatorMatchesTheCapturedIosBuild` | `iPhone OS 27_0_1` / `CriOS/156.0.8078.54` / `webdriver: false` |
| `ScreenAndGeometryAgree` | 屏幕 402×874 **且** viewport 设备宽高一致 |
| `IntlLocaleIsDutch` | `"locale": "nl-NL"` |
| `WindowListsCarryIosOnlyNames` | `gcrweb` / `_injected_programmatic_form_submission_handler` |
| `PixelTablesAreRgbaQuadruples` | 每张表 ≥16 个值，全部在 0–255 |
| `WebglTablesCoverBothContexts` | `webgl` **和** `webgl2` 都在 |
| `CanvasTableHoldsAnActualPng` | `data:image/png;base64,iVBORw0KGgo` 且 >400 字符 |
| `CredentialShimDisguisesItsSource` | 有 `src` / `name` / `length` |

**`ScreenAndGeometryAgree` 挡的是「内部不一致」**：屏幕 402×874 但 viewport 写成 390×844，
两个值单独看都合理，一起看就是矛盾——那是最容易被抓的一种。

**`PixelTablesAreRgbaQuadruples` 挡的是「填了假数字」**：一个 2×2 的 RGBA 读取是 16 个 0–255 的值。

### 不补的部分

**不做一个 `DeviceProfile` C# 类去解析这 29 张表。**

理由是这轮学到的：

- 这些表**是 JS 的数据**，它们的消费者是 `hcaptcha-spoof.js` 本身
- 在 C# 里再表示一遍，等于**把同一份数据抄到第二个地方**，而原版没有第二个地方
- 抄过去之后，两份数据会漂移——这正是 R134 注释里作者写的那句
  **「hand-edits are lost and drift is how the last one died」**

**测试读的就是那个 JS 文件本身。** 一份数据，一个来源。

### 验证

```
dotnet test      631 通过 / 0 失败 / 2 跳过   (+9)
live contracts   PASS
store modules    PASS 61 registered
```

---
