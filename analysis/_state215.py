import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 一、现在在哪')
head = '''最后更新：第 215 轮（CustomBrowser 转正：**notBuilt 归零 —— 原版 87 个视图类一个不缺**；1398 绿）。

---


## 重启后从这里继续（R215 收尾快照）

**里程碑**：`OriginalViewClassParityTests` 的账本现在是 **same=75 / renamed=12 / notBuilt=0（total 87）**。
`NotBuiltYet` 为空，测试里写着 `Assert.Empty(NotBuiltYet)` —— 以后谁删掉一个实现会立刻变红。

**R215 做的**：`Views/Browser/CustomBrowser.cs`（locale 的 `Browser.Header/AddressBar/Autofill/NewTab`），
动作经 `CustomBrowserActions` 委托转给 `ChromiumBridge.NavigateAsync/EvaluateAsync`，所以视图可脱离 Chromium 测试。
**窗口上明确写着它没有绘制视口**（headless CDP），不假装。入口：`Cybersole.exe --browser [url]`，
解析抽成 `App.WantsBrowserWindow` / `App.BrowserUrl`（可测）。

**三条数**：same 75 / renamed 12 / notBuilt 0；UI 类 97（PARITY.md：83 = 26 Window + 57 UserControl）。

**四个数字要一起改**（每次都会响）：`OriginalViewClassParityTests` 的 same/notBuilt、
`SummaryBlockTests` 读的 VERDICT 指南（UI 类数 / 不可达数）、`ParityDocTests` 读的 PARITY.md（Window/UserControl 数）。

**先跑什么**：

```powershell
cd D:\\projects\\cyber-reverse\\replica
& 'D:\\tools\\dotnet8\\dotnet.exe' test tests\\Cybersole.Tests\\Cybersole.Tests.csproj -c Debug --no-restore `
    --nologo -v q --filter "Speed!=Slow"        # 1398 通过 / 0 失败 / 2 跳过
```

**环境纪律**：测试已静音（`CYBERSOLE_SILENT`）；跑完清 `cyb-chromium` 进程与临时目录；
`Repurposed ≥ 2.5 GB` 或 Commit ≥ 30 GB 就重启（收尾时 Commit 约 40 GB，**强烈建议下次开工前重启**）。

**下一步候选**（视图账本已清空，接下来是"深"而不是"全"）：
1. `mutation-check` 补跑（重启后）
2. General 面板细节：Monitor Concurrency 一行形态、Startup Page/Currency 的 (i) 行
3. 六条流程序号缺口（受 R206 负结果限制，只能靠序号重合证据）
4. 用 cua 把目标窗口再量一轮，重点看本次新写的三个窗口（Splash / Login / Browser）与真机的差异

## 一、现在在哪'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j + len('## 一、现在在哪'):]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
