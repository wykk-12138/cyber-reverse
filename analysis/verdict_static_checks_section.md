### 把两类「代码看着对」的缺陷变成断言

R122 收尾时列了一张表：45 个缺陷里有 6 个是「同一类型在第二个文件重演」。
**三类有了机械检查（死按钮、乱码、跨线程 await），两类没有**——这轮补上。

### 一、「后写赢」

**形状**：`catch` 写了一句话，`catch` 之后的下一句无条件写同一个控件。

```csharp
try { Process.Start(...); }
catch (Exception ex) { _status.Text = $"cannot open browser: {ex.Message}"; }
_status.Text = "browser opened — paste the authorization code below";   // ← 覆盖
```

**R103 的 `Tasks`、R122 的 `SignIn` 都是这个。**

检查方式：找到 `catch` 块，读它写了哪些接收者（`_status` / `Status` / `_result` …），
再看块结束后的第一条非空非注释语句是不是写同一个接收者。

**扫全库：0 处。** 两条都修过了。

还加了一条更窄的：**单行 `catch { … }` 紧跟一句写同一接收者**——那是 R122 的原始布局。

**两条都进测试。**

### 二、「改 A 保存 B」

**形状**：UI 字段持有一个新建的配置对象，而同一文件里又调 `Config.Save()`。

```csharp
private readonly SolverSettings _settings = new();    // ← 一次性对象
…
setter(cb.IsChecked ?? false);                        // 改这个
_services.Config.Save();                              // 保存另一个
```

**R113 的 `CaptchaProviders`、R122 的 `SolverWindow` 都是这个。**

检查方式：正则 `private (readonly)? <Xxx>Settings|Config|Options|Document> name = new(`，
且文件里出现 `Config.Save()`。

**扫全库：0 处。**

### 为什么这两条能机械化

**它们都是「文本形状」而不是「语义错误」。**

| 缺陷 | 判据 | 可否机械 |
|---|---|---|
| 死按钮 | `Button("X", () => Status("..."))` | ✅ |
| 乱码 | CJK 字符紧跟 `?` | ✅ |
| 跨线程 await | `await _services.*` 无 `ConfigureAwait` | ✅ |
| 后写赢 | catch 之后写同一接收者 | ✅ |
| 改 A 保存 B | 一次性配置对象 + `Config.Save()` | ✅（有假阳性风险） |
| 表单被忽略 | 需要知道哪些控件属于哪个按钮 | ❌ |
| 协议用错 | 需要发一次真实请求 | ❌ |

**前三类判据是「语法」，这两类判据是「相邻」**——相邻关系也是文本的。

**剩下两类真的需要运行**：一个是控件与按钮的绑定关系，一个是服务器的响应。

### 一个副作用：测试自己也会写错

写第一个版本时我把 `SuccessLineIsNotOutsideItsTry` 的方法签名删掉了，
函数体成了孤儿，编译报 `应输入类型、命名空间定义或文件尾`。

**这不是测试发现了 bug，是测试自己就是 bug。** 重写了整个文件。

**和 R112 那三次「在禁止乱码的地方写乱码」同源**：**写检查的人最容易犯被检查的错。**

### 现在的静态检查清单

| 测试 | 挡什么 | 数量 |
|---|---|---|
| `DeadButtonTests` | 只有 `Status(...)` 的按钮 | 12 个已知 |
| `SourceEncodingTests` | 乱码 / 粘连注释符 | 0 |
| `UiContinuationTests` | 跨层 await 无 `ConfigureAwait` | 0 |
| `StatusOverwriteTests` | 后写赢 ×2 / 一次性配置对象 | 0 |

**四条测试，零失败，全部是「以后新增代码会被挡住」而不是「历史问题已修完」。**

### 验证

```
dotnet test      583 通过 / 0 失败 / 2 跳过   (+3)
live contracts   PASS
store modules    PASS 61 registered
```

---
