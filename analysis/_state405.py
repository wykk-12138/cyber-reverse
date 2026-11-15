import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 405 轮：把 R387 的教训变成一条**结构约束**

### 一、先查还有没有别的写口

`AppPaths` 里除 `DataRoot` 外还有 `LocalRoot`（= `%LOCALAPPDATA%\\Cybersole`，原版的安装/缓存目录）。
查它的读者：只有设置页的版本面板，**只读**（数 `packages` 里有几个包）。

结论：没有第二个"写进原版目录"的漏洞，但**没人防止以后出现**。

### 二、所以加了两样东西

```csharp
public static IReadOnlyList<string> WritablePaths { get; } = new[]
{
    Settings, Accounts, Tasks, Proxies, Billing, Solvers, Analytics, Sessions,
    SmartActions, SmartActionUtilities, BackupsDir, LogsDir, BrowserDataDir, ChromiumDir, TelemetryDir,
};
```

外加守卫 `EverythingTheReplicaWritesStaysUnderItsOwnDataRoot`：
**每一条可写路径都必须落在 `DataRoot` 之下**，且 `LocalRoot` 不能出现在这份清单里。

`LocalRoot` 的注释也改成明确写着"只读，只有版本面板读它"。

### 三、验证

```
LiveSchemaPinsTests + BindingGapRatchetTests   13 通过 / 0 失败
```

### 四、这一轮的一句话

> R387 我是靠"发现文件里出现了我自己的测试组名"才醒悟的 —— 那是运气。

> **把教训写成断言，下一次就不用靠运气。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''```
复刻件   %APPDATA%\\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\\Cybersole             （只读证据，永不写入）
```''', '''```
复刻件   %APPDATA%\\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\\Cybersole             （OriginalDataRoot，只读证据，永不写入）
原版安装 %LOCALAPPDATA%\\Cybersole        （LocalRoot，只读；只有版本面板数包）
```

守卫：`EverythingTheReplicaWritesStaysUnderItsOwnDataRoot` —— 15 条可写路径必须都在 `DataRoot` 下。''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
