import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 一、现在在哪')
head = '''最后更新：第 214 轮（SplashWindow 转正：镜像里有它的 axaml 资源名；notBuilt 2→1；1399 绿）。

---


## 重启后从这里继续（R214 收尾快照）

**只剩一个洞：`CustomBrowser`**（内嵌浏览器窗口）。locale 里已有它的四条文案：
`Browser.Header`="Browser"、`Browser.AddressBar`="Search or enter address"、`Browser.Autofill`="Autofill"、`Browser.NewTab`="New Tab"。

**R214 做的**：`Views/Auth/SplashWindow.cs`（无边框 + 渐变背景 `SplashBackground` + 圆形图标 `SplashCyberIcon` +
`Auth.Welcome`="Welcome to Cybersole 5.0" + 版本行），并接进 `Program`：先 Show splash，主窗口 `Opened` 时关掉。
可视树抽成 `SplashWindow.BuildVisual(...)`，因为 **headless 测试构造 `Window` 会抛**
`Unable to locate 'Avalonia.Platform.IWindowingPlatform'` —— 测试只碰可视树。

**三条数**：same 74 / **notBuilt 1（CustomBrowser）** / UI 类 96（PARITY.md：82 = 25 Window + 57 UserControl）。

**文档坑（第二次踩）**：`DocsConsistencyTests` 扫 VERDICT 里所有 `N 条错误/文案` 并要求等于 13；
在文档里**复述**那个错误写法会再次触发。要用别的词（如「条报错」）。

**先跑什么**：

```powershell
cd D:\\projects\\cyber-reverse\\replica
& 'D:\\tools\\dotnet8\\dotnet.exe' test tests\\Cybersole.Tests\\Cybersole.Tests.csproj -c Debug --no-restore `
    --nologo -v q --filter "Speed!=Slow"        # 1399 通过 / 0 失败 / 2 跳过
```

**环境纪律**：测试已静音（`CYBERSOLE_SILENT`）；跑完清 `cyb-chromium` 进程与临时目录；
`Repurposed ≥ 2.5 GB` 或 Commit ≥ 30 GB 就重启（本轮收尾 Commit 约 38 GB，**建议下次开工前重启**）。

**下一步候选**：
1. `CustomBrowser`（最后一块）：窗口 + 地址栏 + New Tab + Autofill，绑定到 `ChromiumBridge.NavigateAsync/EvaluateAsync`
2. General 面板细节：Monitor Concurrency 一行形态、Startup Page/Currency 的 (i) 行
3. 六条流程序号缺口（受 R206 负结果限制）

## 一、现在在哪'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j + len('## 一、现在在哪'):]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
