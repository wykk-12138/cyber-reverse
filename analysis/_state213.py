import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 一、现在在哪')
head = '''最后更新：第 213 轮（LoginControl 转正：界面文案全部来自原版 locale；notBuilt 3→2；1396 绿）。

---


## 重启后从这里继续（R213 收尾快照）

**两块欠账已还（R211-R213）**：
1. `LoginControl`（`Views/Auth/LoginControl.cs`）—— **界面上每一行都是原版 locale 的 `Auth.*` 键**，
   没有一句是编的（`Auth.Welcome` = "Welcome to Cybersole 5.0"、"Sign in with browser"…）。
   账户窗口（CommonModals）新增 **Sign in** 入口，经 `ViewHostModal` 打开，登录成功自动关闭。
2. Billing 左栏用上共享 `GroupGrid`（R211）；Accounts 左栏**明确不用**（两层树），已写成测试钉住。

**三条数**：same 73 / **notBuilt 2（只剩 `SplashWindow` 与 `CustomBrowser`）** / UI 类 95（24 Window + 57 UserControl）。

**顺带修的红灯**：`DocsConsistencyTests` 把 VERDICT 里 `N 条错误/文案` 的说法当数字校验；
R212 我写的「0 条错误」被读成"错误文案只有 0 条"，已改成「0 条 error 级记录」。**文档里的数字会被测试当真。**

**先跑什么**：

```powershell
cd D:\\projects\\cyber-reverse\\replica
& 'D:\\tools\\dotnet8\\dotnet.exe' test tests\\Cybersole.Tests\\Cybersole.Tests.csproj -c Debug --no-restore `
    --nologo -v q --filter "Speed!=Slow"        # 1396 通过 / 0 失败 / 2 跳过
```

**环境纪律（R212 学到的）**：
- 测试进程已静音（`CYBERSOLE_SILENT=1` 由 `SilentTestRun` 设），不再有"后台叮咚"
- 跑完清 `cyb-chromium` 进程与 `%LOCALAPPDATA%\\Temp\\cyb-chromium-*`（R212 清出 46.7 GB 垃圾）
- `Repurposed ≥ 2.5 GB` 或 Commit ≥ 30 GB 就重启；**本轮收尾可用仅 7.9 GB，建议下次开工前重启**

**下一步候选**：
1. 剩下 2 个 notBuilt：`SplashWindow`（启动画面）、`CustomBrowser`（内嵌浏览器窗口，locale 有 `Browser.AddressBar/Autofill/Header/NewTab`）
2. General 面板细节：Monitor Concurrency 一行形态、Startup Page/Currency 的 (i) 行
3. 六条流程序号缺口（受 R206 负结果限制，只能靠序号重合证据）

## 一、现在在哪'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j + len('## 一、现在在哪'):]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
