# 双实例函数清单对照（生成文件，请勿手改）

> 由 `python analysis/func_compare.py` 生成。
> 两条链：原版 `http://127.0.0.1:13337/mcp`、复刻件 `http://127.0.0.1:13338/mcp`（带 PDB 符号）。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-14 18:04:11 +0800 |
| 原版函数总数 | 321244 |
| 原版可命名函数 | 10041 |
| 复刻件函数总数 | 187328 |
| 复刻件可命名函数 | 175104 |
| 差值（复刻件 − 原版） | -133916 |
| 原版 IDB / 镜像 | `D:\projects\cyber-reverse\target\Cybersole.exe.i64` |
| 复刻件 IDB / 镜像 | `D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.exe.i64` |

## 函数大小分布（同口径）

| 区间（字节） | 原版 | 复刻件 |
|---|---|---|
| 0-31 | 117133 | 49992 |
| 32-63 | 54922 | 33964 |
| 64-127 | 65288 | 51525 |
| 128-255 | 46537 | 31605 |
| 256-511 | 21553 | 12420 |
| 512-1023 | 9947 | 4980 |
| 1024-4095 | 5192 | 2582 |
| 4096-99999 | 672 | 260 |

## 绑定表成员在复刻件侧的命中率

| 项 | 值 |
|---|---|
| 绑定成员总数 | 819 |
| 在复刻件镜像里可见（独立符号） | 21 |
| 命中率 | 2.6% |

> **命中率低不等于缺口**：NativeAOT 会内联/裁剪不可达成员，属性 getter 常无独立符号。
> 按 `docs/PARITY_CLAIMS.md` 的证据纪律，看不到 ≠ 不存在，本条整体记 Unknown。

## 复刻件侧可命名函数（分页 0，每页 40，共 175104）

| 地址 | 大小 | 名字 |
|---|---|---|
| `0x140001000` | 29 | `__GetNonGCStaticBase_Acornima_System_StringExtensions` |
| `0x14000101d` | 29 | `__GetNonGCStaticBase_Acornima_Acornima_UnicodeProperties` |
| `0x14000103a` | 29 | `__GetNonGCStaticBase_Acornima_Acornima_Tokenizer_RegExpParser` |
| `0x140001057` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_AvaloniaLocator` |
| `0x140001074` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_StyledElement` |
| `0x140001091` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Visual` |
| `0x1400010ae` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Utilities_StopwatchHelper` |
| `0x1400010cb` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Threading_DispatcherPriority` |
| `0x1400010e8` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Rendering_Composition_Transport_CompositionBatch` |
| `0x140001105` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Rendering_Composition_Server_CompositionProperty` |
| `0x140001122` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Rendering_Composition_Server_ServerCompositionTarget` |
| `0x14000113f` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Layout_Layoutable` |
| `0x14000115c` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_FocusManager` |
| `0x140001179` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_PullGestureRecognizer` |
| `0x140001196` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_Gestures` |
| `0x1400011b3` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_InputElement` |
| `0x1400011d0` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_XYFocus` |
| `0x1400011ed` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Input_GestureRecognizers_ScrollGestureRecognizer` |
| `0x14000120a` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Diagnostics_Diagnostic` |
| `0x140001227` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_DashStyle` |
| `0x140001244` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_Effect` |
| `0x140001261` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_ImmutableBlurEffect` |
| `0x14000127e` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_ImmutableDropShadowEffect` |
| `0x14000129b` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_EllipseGeometry` |
| `0x1400012b8` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_FontFamily` |
| `0x1400012d5` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_Geometry` |
| `0x1400012f2` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_GlyphRun` |
| `0x14000130f` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_KnownColors` |
| `0x14000132c` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_RectangleGeometry` |
| `0x140001349` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_TextDecorations` |
| `0x140001366` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_TextFormatting_Unicode_LineBreakEnumerator` |
| `0x140001383` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_Fonts_Tables_HorizontalHeadTable` |
| `0x1400013a0` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_Fonts_Tables_OS2Table` |
| `0x1400013bd` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Media_Fonts_Tables_Name_NameTable` |
| `0x1400013da` | 29 | `__GetNonGCStaticBase_Avalonia_Base_Avalonia_Animation_Animation` |
| `0x1400013f7` | 29 | `__GetNonGCStaticBase_Avalonia_Controls_Avalonia_Controls_AutoCompleteBox` |
| `0x140001414` | 29 | `__GetNonGCStaticBase_Avalonia_Controls_Avalonia_Controls_Border` |
| `0x140001431` | 29 | `__GetNonGCStaticBase_Avalonia_Controls_Avalonia_Controls_Button` |
| `0x14000144e` | 29 | `__GetNonGCStaticBase_Avalonia_Controls_Avalonia_Controls_ButtonSpinner` |
| `0x14000146b` | 29 | `__GetNonGCStaticBase_Avalonia_Controls_Avalonia_Controls_CalendarDatePicker` |

## 绑定成员未命中的清单（分页 0，每页 40，共 798）

| 类型 | 成员 |
|---|---|
| CreateInfo | Name |
| CreateInfo | Properties |
| Platform | InputType |
| Platform | MultiCart |
| Platform | Name |
| Platform | QuantityAutoAdjustSupport |
| Platform | QuantitySupport |
| CaptchaProvider | ApiKey |
| CaptchaProvider | Balance |
| CaptchaProvider | BalanceSupported |
| CaptchaProvider | Concurrency |
| CaptchaProvider | Count |
| CaptchaProvider | IsFetchingBalance |
| CaptchaProvider | Name |
| CaptchaProvider | Priority |
| CaptchaProvider | Type |
| CloudflareSolver | ApiKey |
| CloudflareSolver | Balance |
| CloudflareSolver | BalanceSupported |
| CloudflareSolver | Concurrency |
| CloudflareSolver | Count |
| CloudflareSolver | Id |
| CloudflareSolver | IsFetchingBalance |
| CloudflareSolver | Name |
| CloudflareSolver | Type |
| Element | Name |
| Element | PropName |
| Settings | AutoOpen3DS |
| Settings | AutoOpen3DSLimit |
| Settings | BackupInterval |
| Settings | BetaUpdates |
| Settings | BrowserLimit |
| Settings | BrowserPath |
| Settings | BrowserProfileAssignment |
| Settings | BrowserWindowMode |
| Settings | Clock |
| Settings | Currency |
| Settings | Keybinds |
| Settings | Language |
| Settings | MaxBackups |

---

## 这两条链能回答什么 / 不能回答什么

**能**：函数数量、各侧可命名数、复刻件名字清单、绑定成员在产物里的可见性、函数大小分布。

**不能**：任意两个函数是否语义等价 —— 那需要**伪代码级**对照（两侧 `decompile` 后对齐），
本次两个实例只做清单级对照。claim C7（逐函数等价）因此记 Unknown，
缺的证据写在 `docs/PARITY_CLAIMS.md`。

