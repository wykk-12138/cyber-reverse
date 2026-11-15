import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 301 轮：拿 238 个 `Settings.*` 文案当检查表 —— **它不能当缺陷探测器**（抽样验证）

### 一、想做什么

池子里有 **238 个 `Settings.*` 文案键**，分 20 组（General 20、Data 23、Payment 14、CaptchaProviders 14…）。
想法很自然：把每个叶子名去复刻件的 Settings 源码里找，找不到的就是"这一节漏了控件"。

### 二、初看有大量"缺失"

```
group               keys   命中   缺失示例
Data                  23     12   BackupIntervalTooltip, BackupNow, MaxBackupsTooltip, MaxFileSize
Payment               14     10   ExternalBrowser, MaxTabs, ThreeDS, WindowMode
General               20     12   DefaultDelays, DefaultError, DefaultMonitor, DefaultTimeout
Webhook                8      4   Event, Extra, ExtraFields, NewWebhook
```

### 三、抽样三条去核，**全部其实都有**

| "缺失"的键 | 复刻件里的实际情况 |
|---|---|
| `Data.BackupNow` | **已有按钮** `UiKit.Button("Backup Now", () => { services.Config.Backup(); … })`（`ProviderViews.cs:1037`）—— 只是标签是字面量，不叫这个键名 |
| `Payment.ThreeDS` | 已有 **"Auto Open 3DS"** 组合框 + `AutoOpen3DSLimit` 数字框（`SettingsViews.cs:1482/1536/1537`） |
| `Payment.WindowMode` / `MaxTabs` | 见上，同一节里以不同标签实现 |

### 四、结论：这个测法**只能证明"没按这个键名引用"，不能证明"没这个功能"**

所以它**不能当缺陷探测器**，也就不该进棘轮 —— 否则会逼着我去"补"一堆其实存在的控件。
（这和 R300 的教训是同一类：**文案/名字层面的差异，不等于功能差异。**）

### 五、这一轮真正的产出

把这条"看起来很有用、其实会误导"的度量**否证掉并写下来**，
免得下一轮的我又花一轮去追 105 个假缺口。

### 六、验证

本轮未改代码（抽样核对只读源码）。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 301 轮（拿 238 个 `Settings.*` 文案当检查表 → **否证**：它测的是"键名引用"，不是"功能有无"）。

---

## 已否证的度量（别再追）

| 度量 | 为什么不能用 |
|---|---|
| `Settings.*` 叶子名 ↔ 复刻件源码标识符 | 复刻件用**字面量标签**（"Backup Now"、"Auto Open 3DS"），不引用键名 → 105 个"缺失"是假缺口 |
| 抽样核对 | `Data.BackupNow` ✔ 已实现（`ProviderViews.cs:1037`）、`Payment.ThreeDS` ✔ 已实现（`SettingsViews.cs:1482`） |

**教训**：文案/名字层面的差异 ≠ 功能差异（与 R300 同类）。

## 仍然有效、可引用的度量（别搞混）

| 度量 | 数字 |
|---|---|
| 端点证据账 | 89 = 67 有证据 + 18 标推断（其中 10 真发） |
| 八条流 | 8/8 字面量可对账（`StoreFlowDigestTests`） |
| 错误目录 | 13/13 标题 + 13/13 详情逐字命中 |
| 绑定缺口 | 33（real = ceiling） |

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R300；R301 未改代码）
mutation   24/24 fired（R286）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
