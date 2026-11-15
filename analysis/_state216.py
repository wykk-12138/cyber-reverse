import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 一、现在在哪')
head = '''最后更新：第 216 轮（General 面板按窗口改成单行 + 两条 (i) 独立行；本轮只跑 24 个设置测试，完整套件与 mutation-check 欠着）。

---


## ⚠️ 欠着两件事（重启后先做）

1. **完整套件** `Speed!=Slow`（上一轮基线 1399 通过 / 0 失败 / 2 跳过）
2. **`mutation-check`**（上次 23 条守卫全开、restored GREEN）

原因：收尾时 `Commit 43 GB / 可用 5.25 GB`，越过内存红线。按 `MEMORY_DISCIPLINE.md` 不许再跑重活。
R216 的改动只用受影响的 24 个设置测试验证过（全绿、156 ms、没有拉起浏览器）。

---

## 重启后从这里继续（R216 收尾快照）

**里程碑（R215）**：视图账本 `same=75 / renamed=12 / notBuilt=0（total 87）`，`NotBuiltYet` 为空。

**R216 做的**：General 面板按窗口改成
`(i) Monitor Concurrency [模式▾][数字框]` **单行** + `(i) Startup Page` / `(i) Currency` 各自独立成行；
`Enable clock` / `Clock format` 保留但单独成卡（窗口截图在 Currency 处截断，所以只断言"不同卡"）。
**认知修正**：`Ratio` 是 `MonitorConcurrency` 的一个**模式取值**，不是一行。

**先跑什么**：

```powershell
cd D:\\projects\\cyber-reverse\\replica
& 'D:\\tools\\dotnet8\\dotnet.exe' test tests\\Cybersole.Tests\\Cybersole.Tests.csproj -c Debug --no-restore `
    --nologo -v q --filter "Speed!=Slow"          # 期待 1400 通过 / 0 失败 / 2 跳过
& 'D:\\projects\\IDA-pro\\python311\\python.exe' tools\\mutation-check.py
```

**环境纪律**：测试已静音（`CYBERSOLE_SILENT`）；跑完清 `cyb-chromium` 进程与临时目录；
`Repurposed ≥ 2.5 GB` 或 `Commit ≥ 30 GB` 就重启。

**下一步候选**：
1. 重启后补上面那两笔
2. 用 cua 把 R213-R215 新写的三个窗口（Splash / Login / Browser）跟真机量一遍
3. 六条流程序号缺口（受 R206 负结果限制）

## 一、现在在哪'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j + len('## 一、现在在哪'):]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
