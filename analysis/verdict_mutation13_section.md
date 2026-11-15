### 13 条变异，全部 fired —— 而且过程中揪出第二个假守护

R144 把变异表扩到 8 条。这一轮加到 13 条，**过程中有三个变异编译不过、一个守护是假的**。

### 先修工具：区分「编译失败」和「测试失败」

第一轮跑出 `13 fired`，其中三个**没有 `失败!` 行**。查下去是编译错误：

```
round 124 -- a cross-layer await:  error CS4008: 无法等待"void"
round 124 -- a throwaway settings: error CS1514: 应为 {
```

**编译不过也会让 `dotnet test` 非零退出，而守护根本没运行。**

加一个分类函数：

```python
def classify(code, tail):
    joined = "\n".join(tail)
    if "error CS" in joined:
        return "DID NOT COMPILE — the guard never ran"
    if code == 0:
        return "GUARD IS DECORATIVE — tests stayed green"
    return "guard fired"
```

**这三种「红」在原来的 summary 里长得一模一样。**

### 五个新变异，各打一种判据形状

| 变异 | 判据类型 | 第一轮结果 |
|---|---|---|
| 新写一个死按钮 | **模式匹配** | 编译失败 → 修好后 fired |
| 跨层 await 丢掉 `ConfigureAwait` | **模式匹配** | 编译失败 → 修好后 fired |
| 往注释里写一个乱码序列 | **字节匹配** | fired |
| 加一个一次性 settings 字段 | **模式匹配** | **GREEN（假守护）** |
| 从 csproj 删一个引擎资产 | **资源清单** | fired |

### 每个编译失败都指向一个真实约束

**一、`await _services.Config.Load()`** —— `Load()` 返回 `void`。

`UiContinuationTests` 找的是 `await <services>`。但 `AppServices` 上没有哪个成员是「随便能 await 的」。
最后用**真实存在的那一处**：

```python
"find": "}).ConfigureAwait(true);",
"replace": "});",
```

`SolverWindow` 第 197 行本来就有 `await _services.Captcha.SolveAsync(…).ConfigureAwait(true)`。
**删掉那个 `.ConfigureAwait(true)`，正是 R122 修过的缺陷原形。**

**二、字段插错位置** —— `public sealed class SolverWindow : Window` 后面紧跟 `{`，
我把字段插在两者之间。改成 anchor 包含 `{`。

### 第二个假守护

```
GUARD IS DECORATIVE — tests stayed green   round 124 -- a throwaway settings object beside Config.Save
```

`NoUiFieldHoldsAThrowawaySettingsObjectWhileSaving` 的正则是：

```csharp
@"private\s+(?:readonly\s+)?([A-Z]\w*(?:Settings|Config|Options|Document))\s+\w+\s*=\s*new\s*\("
```

**`[A-Z]\w*` 不含点。** 所以：

```csharp
private readonly SolverSettings _throwaway = new();               // 匹配
private readonly Cybersole.Core.Models.SolverSettings _t = new(); // 不匹配
```

**同一个 bug，两种写法，只抓一种。**

而我第一版变异恰好用了全限定名——**变异自己撞上了缺陷，所以测试是绿的**。

**修判据**：`[A-Z][\w.]*`。

**然后变异改用简单名**（那更贴近原 bug 的形态），测试也覆盖两种写法。

### 13/13

```
guard fired   round 136 × 3（contentWindow / createElement / 裸全局）
guard fired   round 137 / 138
guard fired   round 127 / 133
guard fired   round 124 × 3（catch 覆盖 / 死按钮 / 一次性对象）
guard fired   round 122 / 112 / 134
restored tree: GREEN
```

### `verify.ps1` 现在是四个分支

| 情况 | 报告 |
|---|---|
| `decorative > 0` | **FAIL** — 有守护是假的 |
| `nocompile > 0` | **FAIL** — 「a mutation that does not build proves nothing」 |
| `fired == 0` | **WARN** — 锚点全失效 |
| 其他 | **PASS** |

**第二个分支是这一轮的教训本身**：编译失败看起来和测试失败一样，都是红的。

```
powershell -File tools\verify.ps1 -Full
  unit tests         PASS   exit 0
  mutation guards    PASS   13 fired, 0 decorative, 0 did-not-compile, 0 skipped
  VERDICT: all checks passed
```

---

## 四个假阳性，四种不同的原因

| 轮次 | 假象 | 原因 |
|---|---|---|
| R143 | 测试绿，bug 在 | 断言只查「词出现过」 |
| R144 | `16 fired` 实际 8 | 数词而非数事 |
| R145 | `13 fired` 实际 10 | 编译失败被当成测试失败 |
| R145 | 测试绿，bug 在 | **正则漏了一种合法写法** |

**四次都发生在「我以为我在检查」和「我实际检查了」之间。**

**第一次是断言写弱了，第二次是计数写错了，第三次是分类写漏了，第四次是判据写窄了。**
**四种不同的技术错误，一个共同的判断错误：把「看起来对」当成了「检查过」。**

## 下一步

13 条覆盖了 R112 / R122 / R124 / R127 / R133 / R134 / R136 / R137 / R138 九轮的修复。

**还没进表的**：`DeviceTableTests`（R135 的 29 张设备表）、`LocaleDictionaryTests` 的键集断言、
`EngineAssetsTests` 的厂商签名断言。

下轮加完，然后**把「新增一条修复必须同时新增一条变异」写进 `docs/HISTORY.md`**——
**否则这套工具下一轮就会被人忘记。**

用户目标保持 active。
