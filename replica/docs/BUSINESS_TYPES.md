# 业务类型覆盖（生成物 —— 不要手改）

由 `python tools/business_types.py` 生成。

**为什么用前缀分离**：R1066 说「BCL 与业务不可分」，那说得过头了 ——
镜像的反射元数据带**全限定类型名**，而它自己的类型都在 `Cybersole.` 下。
**按命名空间归属分，就是那个分离**，不需要函数名。

## 一、对照

| 对照串 | 命中 |
|---|---|
| `kpsdk` | **17** |
| `Cybersole.` **分片查询次数** | **26** |

**→ 对照成立。**

## 二、两个数

| 侧 | 业务类型数 | 命名空间数 |
|---|---|---|
| **原版**（元数据） | **122** | 31 |
| **复刻件**（源码） | **648** | 53 |

## 三、按简单类型名对

| 类别 | 数 |
|---|---|
| 两边都有（同名） | **109** |
| 只在原版 | **13** |
| 只在复刻件 | **534** |

**→ 「只在原版」不是缺口**：goal 明说「命名可不同」，而这一列里有一大部分是复刻件用了自己的名字。
→ 而「两边都有」那 109 个同名类型，才是可以用名字对字段的（见 `TYPE_COVERAGE.md`）。

## 四、原版命名空间的前 20 个（按类型数）

| 命名空间 | 类型数 |
|---|---|
| `Cybersole.Ui.Views.Settings` | **19** | ✓
| `Cybersole.Models` | **13** | ✓
| `Cybersole.Ui.Views.SmartActions` | **11** | ✓
| `Cybersole.Ui.Views.Settings.Modals` | **10** | ✓
| `Cybersole.Ui.Views.Profiles.Modals` | **8** | ✓
| `Cybersole.Ui.Views.Modals` | **5** | ✓
| `Cybersole.Ui.Views.Tasks.Modals` | **5** |
| `Cybersole.Ui.Views.Accounts` | **4** | ✓
| `Cybersole.SmartActions` | **4** | ✓
| `Cybersole.Ui.Views.Tasks` | **4** | ✓
| `Cybersole.Ui.Localization` | **4** |
| `Cybersole.Ui.Views.Analytics.Modals` | **4** | ✓
| `Cybersole.Ui.Views.Accounts.Modals` | **3** |
| `Cybersole.Ui.Views.Auth` | **3** | ✓
| `Cybersole.Ui.Views.Captcha` | **3** | ✓
| `Cybersole.Ui.Views.Proxies.Modals` | **2** |
| `Cybersole.Services` | **2** | ✓
| `Cybersole.Ui.Controls` | **2** |
| `Cybersole.Ui.Views.Utilities` | **2** | ✓
| `Cybersole.Ui.Views.Monitor` | **2** | ✓

**→ ✓ 表示复刻件里也有同名命名空间。**

## 五、边界

- **原版侧是元数据，不是源码**：只算有属性访问器的类型 ⇒ 纯静态类、纯枚举会漏 ⇒ **原版侧是下界**。
- **复刻件侧是源码**：`class`/`record`/`struct`/`enum`/`interface` 都算，比元数据宽。
- **只按简单名对**：`A.Thing` 与 `B.Thing` 会被当成同名，而那可能是两个不同的类型。
- **不比较行为**：类型数齐了不等于功能等。
