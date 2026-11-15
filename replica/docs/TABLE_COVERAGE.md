# 目标脚本的 40 张表：接线台账（R199）

`Cybersole.exe` 里注入的那段脚本有 **40 个** `const X = [...] / {...} / new Set(...)` 声明。
这张表逐条记录：它在原版的哪个偏移、现在在复刻件里的哪个位置、状态如何。

- **wired** = 数据逐字节抄进来，且代码在用
- **derived** = 不单独存表，运行时从别的表推出来（原版也是这么做的）
- **duplicate** = 与另一处已接线的常量重复，复刻件只保留一份

| # | 表 | 偏移 | 体量 | 状态 | 复刻件位置 |
|---|---|---|---|---|---|
| 1 | `PATCHES` | `0x03d06d69` | 23 | wired | `PatchJournal`（`G.__patchJournal.patches`） |
| 2 | `KNOWN` | `0x03d06d82` | 90 | wired | `PatchJournal.Known`（剔除 `Object`/`Reflect`，R191） |
| 3 | `INTL_NAMES` | `0x03d070b1` | 84 | wired | `PatchJournal.IntlNames` |
| 4 | `MESSAGES` | `0x03d0969e` | 320 | wired | `EngineParity.Messages` |
| 5 | `ORDER` | `0x03d0a9c6` | 17.7 KB | wired | `KeyOrderRules.OrderRulesJs`（R188） |
| 6 | `WINDOW_ALL` | `0x03d0f9d0` | 19.8 KB | wired | `WindowNameTable.All`（R192 起作为 topList 的 base） |
| 7 | `WINDOW_ENUM` | `0x03d14741` | 3.6 KB | wired | `WindowNameTable.Enum` |
| 8 | `CSS_DECL` | `0x03d15574` | 191 | wired | `KeyOrderRules.CssDeclarationJs` |
| 9 | `CSS_VOCAB` | `0x03d15762` | 30.5 KB | wired | `CssProperties.PropsJs`（R189） |
| 10 | `MAIN_FRAME_ONLY` | `0x03d1de57` | 89 | wired | `KeyOrderTable.MainFrameOnly` |
| 11 | `NAV` | `0x03d1fada` | 674 | wired | `MobileNavigator.Captured` |
| 12 | `NAV_KEYS` | `0x03d1fd7e` | 785 | wired | `NavPrune.AllowList` |
| 13 | `NAV_ORDER` | `0x03d20091` | 777 | wired | `NavOrder.Navigator`（50 名） |
| 14 | `CRED_SHIM` | `0x03d2039c` | 878 | wired | `ForwardingShims` + `NativeArity` |
| 15 | `DEVICE_GLOBALS` | `0x03d222f2` | 19.8 KB | derived | `GlobalPrune` 用 `WindowNameTable.All` 现建 Set |
| 16 | `KEEP` | `0x03d27070` | 100 | wired | `GlobalPrune.Keep` |
| 17 | `HANDLERS` | `0x03d281c8` | 2.1 KB | wired | `HandlerTable.HandlersJs`（R196） |
| 18 | `SCREEN` | `0x03d2975a` | 155 | wired | `MobileSurface`（screen 值） |
| 19 | `SCREEN_ORDER` | `0x03d297f7` | 142 | wired | `NavOrder.Screen` |
| 20 | `SCREEN_KEYS` | `0x03d29887` | 46 | wired | `NavPrune` / `SurfaceOrder` 的 screen 规则 |
| 21 | `VV` | `0x03d2a4de` | 77 | duplicate | `MobileSurface.VisualViewportFields`（同一组值，R151 已接线） |
| 22 | `QUERIES` | `0x03d2bb1b` | 1.5 KB | wired | `MediaQueryTable.QueriesJs`（R197） |
| 23 | `GEOMETRY` | `0x03d2c7f1` | 239 | wired | `MediaQueryTable.GeometryJs` |
| 24 | `GL_PARAMS` | `0x03d2d6a3` | 4.0 KB | wired | `WebGlTable.ParamsJs`（R195，85/135） |
| 25 | `GL_META` | `0x03d2e69b` | 4.5 KB | wired | `WebGlTable.MetaJs`（39/36 扩展） |
| 26 | `FONTS` | `0x03d30964` | **≈100 KB** | wired | `FontMediaTable.FontsJs`（221 条，R198） |
| 27 | `FONTS_LOOSE` | `0x03d58452` | 27 | derived | 运行时由 `unquote()` 建索引 |
| 28 | `CANVAS` | `0x03d58789` | 14.4 KB | wired | `CanvasTable.CanvasJs`（R194） |
| 29 | `PROGRAMS` | `0x03d5cff0` | 22 | wired | `CanvasTable.ProgramsJs`（4 段签名键） |
| 30 | `PIXELS` | `0x03d646ef` | 29 | derived | 运行时 `new Map()`，解码返回的 PNG |
| 31 | `BLINK_2X2` | `0x03d6470e` | 100 | wired | `CanvasTable.Blink2x2Js` |
| 32 | `DEVICE_2X2` | `0x03d64774` | 101 | wired | `CanvasTable.Device2x2Js` |
| 33 | `MEDIA` | `0x03d81751` | 2.1 KB | wired | `FontMediaTable.MediaJs`（18 行，R198） |
| 34 | `CSS_PROPS` | `0x03d82e0c` | 30.5 KB | wired | `CssProperties.PropsJs`（1468 名） |
| 35 | `INTL` | `0x03d8d3ed` | 118 | wired | locale/timezone 层（`SessionPayload` + Intl 补丁） |
| 36 | `GLOBAL_KINDS` | `0x03d927bc` | 3.2 KB | wired | `GlobalSurfaceTable.KindsJs`（R193，67 行） |
| 37 | `GLOBAL_NOT_FN` | `0x03d9343c` | 3.5 KB | wired | `GlobalSurfaceTable.NotFunctionJs`（219 名） |
| 38 | `ENUMERABLE` | `0x03d941e7` | 44 | derived | `new Set(WINDOW_ENUM)` |
| 39 | `INJECTED_GLOBALS` | `0x03d9433d` | 49 | wired | `GlobalSurfaceTable.InjectedGlobalsJs`（`['webkit']`） |
| 40 | `VOICES` | `0x03d95f0e` | 9.0 KB | wired | `VoiceTable.VoicesJs`（**68 个 Apple 声音**，R199） |

## 台账查出来的两件事

**1. `VOICES` 一直没接线。** 复刻件的 `speechSynthesis.getVoices()` 答的是 6 个 Windows/Google 声音
（`Microsoft David` / `Google US English`），而设备是 **68 个 `com.apple.voice.*`**。这比"没有声音"更响 ——
数量、URI、locale 三样同时与 persona 矛盾。R199 换成表之后实测：

```
raw     = [0, "", "", "", 0, "", true, 0]                                   ← headless：零声音
patched = [68, "Ellen", "com.apple.voice.super-compact.nl-BE.Ellen", "nl-BE", 68, "Ellen", true, 1]
```

**2. `FONTS` 的真实体量是 ≈100 KB**，不是早前按首行长度记的 1 KB。221 条 × 每条约 450 字符。

## 台账之外的部分

原版脚本里还有大量**逻辑**（不是表）：错误消息改写、`reseat`、`reorder`、Proxy、`method()` 记录器、
realm 重放、时间/时区、音频、storage 估算……这些按轮次逐个接线，记录在 `VERDICT.md` 的对应章节。
