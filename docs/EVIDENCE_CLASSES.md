# 原版证据种类总表（先枚举，再数）

> R725。**存在理由**：R721–R724 连续四轮都在「数完才发现漏了一类来源」——
> `sub_14XXXXXX` 写法、`[InlineData]` 隔断文档块、池中文案、原版磁盘数据。
> 每次补完标记集数字都往上涨。**根因不是标记集写得不全，是量之前没先枚举来源。**
>
> 这张表就是那一步：**先把原版能提供什么证据列全**，再谈数什么。

## 一、总表

| # | 证据类 | 载体 | 可得性 | 在用？ | 红线 |
|---|---|---|---|---|---|
| 1 | 二进制字节 | `target\Cybersole.exe`（PE 节、`.pdata`、导入、TLS 回调） | 完全 | **是** | 无 |
| 2 | 反编译伪代码 | IDA Hex-Rays（`analysis/ida.py dec`） | 完全 | **是**（主参照） | 无 |
| 3 | 字符串池 | `analysis/pe_strings.txt`、`idautils.Strings()` | 完全（但**打包 blob 内的片段取不干净**） | **是** | 无 |
| 4 | 编译期 XAML 描述符 | 从 #3 索引出的 1,457 条 `${Namespace.Type},${Owner.Member}!{Getter\|Setter\|Property}` | 完全 | **是** | 无 |
| 5 | locale 目录 | 从 #3 抽出的 1,142 条键值 | 完全 | **是** | 无 |
| 6 | **原版磁盘数据** | `%APPDATA%\Cybersole`（5500 个文件）、`%LOCALAPPDATA%\Cybersole`（12 个） | 可读 | **部分**（只用过 `settings.json` 的键码） | **只读，禁写** |
| 7 | **第二版本** | `%LOCALAPPDATA%\Cybersole\current\Cybersole.exe` = **5.18.35.0**，129,306,192 B，md5 `30eef212…` | 可读 | **从未用于本任务** | 只读 |
| 8 | 网络抓包 | 无既有抓包文件 | **无** | 否 | 无 |
| 9 | 运行期观察 | 需登录凭据 | **不可得（YG 那一类）** | 否 | — |
| 10 | 调用图 / 入度 | `idautils.XrefsTo` 逐函数 | 可算但慢（321,244 个） | 试过，**判据被证否**（R719：选出的是胶水） | 无 |

## 二、两个版本的身份（R725 实测）

```
target\Cybersole.exe                         5.18.32.0  129,243,216  md5 f81070a1b90857c0c868336dcd7f0d58
%LOCALAPPDATA%\Cybersole\current\Cybersole.exe 5.18.35.0  129,306,192  md5 30eef212c3a4e96bb0e744743b355bd6
差值                                                       +62,976
```

复算命令：

```powershell
Get-FileHash target\Cybersole.exe -Algorithm MD5
(Get-Item target\Cybersole.exe).VersionInfo.FileVersion
```

## 三、为什么第 7 类（第二版本）重要

本任务要 1:1 复刻的是 **5.18.32**。盘上还有一个 **5.18.35**。**两个版本的差分能回答一个 C7c 一直答不了的问题：**

- **两版完全相同的函数** = 一个真实版本增量里都没动过的核心 → **稳定的见证目标**
- **两版不同的函数** = 版本特有逻辑 → 拿它当"功能对等"的证人**不具代表性**
- 而且差分给出**一份外部事实**：官方到底改了什么。**这是没有符号、跑不起来的情况下，唯一能拿到的第三方校验。**

**工具已经白名单化**（AGENTS.md §1，只读）：

```
D:\projects\IDA-pro\python311\python.exe D:\projects\exe-reverse\skills\exe-reverse\scripts\pe_diff.py <A> <B>
```

R431 用过一次，结论是「5.18.32 ↔ 5.18.35 六节全重排」—— **当时只当版本分诊用，没当复刻证据用。**

## 四、第 6 类的边界（红线复述）

- `%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` **只读**，永不写入。
- 有守卫 `EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` 看着。
- **复刻件自己写出的 `settings.json` / `tasks.json` / `solvers.json` / `checkoutHistory.json` 永远不算证据**（循环论证，R387 踩过）。

## 五、第 6 类里我还没用的东西（本轮盘点）

`%APPDATA%\Cybersole` 5500 个文件，其中大部分是 Chromium 运行时（`chrome.dll` 312 MB 等），**不是程序逻辑**。
真正可能含程序行为证据的是**程序自己写的数据文件**，但本轮只确认了目录存在与文件量，**没有逐个甄别**。
**这是一个待办，不是一个结论。**

## 六、这张表和「测试溯源」的关系

`docs/TEST_PROVENANCE.md` 量的是**复刻件的 1553 条测试用了哪类证据**。
本表量的是**原版一共能给哪几类**。

**两者相乘才是 C7c 的真实覆盖**：只有「测试用了某类证据」而「该类证据被枚举过」，那个数字才可信。
R721–R724 的问题正是**没有先做本表**，所以 TEST_PROVENANCE 的分母一直在动。

## 七、仍然 Unknown

- 第 8 类（抓包）是否真的一个文件都没有：**Unknown**（只看了两个数据目录，没全域搜）。
- 第 6 类里哪些文件是「程序自己写的」而非「浏览器写的」：**Unknown**（未甄别 5500 个文件）。
- 第 7 类能覆盖多少个函数：**Unknown**（差分未跑）。
