# IDA Pro 启动清单（原版 `target\Cybersole.exe`）

> 这份清单存在的原因：我在同一个地方反复踩坑。启动 IDA 不是「打开一个程序」，
> 是**点掉两个模态框 + 等库加载**。漏一个，插件就永远不启，端口 13337 永远拒绝，
> 而 `ida-mcp-doctor.ps1` 只会报 "no listener after 180s"，看起来像 DSH 坏了。

## 一、命令

```powershell
powershell -NoProfile -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 `
    -Path "D:\projects\cyber-reverse\target\Cybersole.exe"
```

**它会超时报失败（exit 1），但那不代表没用** —— 它把 IDA 起来了，接下来要点模态框。

## 二、必须点掉的两个模态框

IDB 已存在（`target\Cybersole.exe.i64`，1.44 GB，已分析完）时，顺序是：

| # | 标题 | 文本（摘要） | **点哪个** | 为什么 |
|---|---|---|---|---|
| 1 | 请确认 | `Database ...i64 already exists. Do you want to overwrite it?` | **加载现有(L)** | 覆盖会丢掉已分析好的库，重建要几小时 |
| 2 | 请确认 | `IDA has found an unpacked version ... It appears IDA did not close properly` | **Restore packed base** | 上次崩溃留下不一致的解包文件；IDA 自己建议从打包库重来 |

**窗口 id 每次都会变**（`list_windows` 看到的 `window_id` 不同），所以每次都要重新读窗口状态，
不能复用上次的 element_token。

## 三、判定就绪

```powershell
python analysis\ida.py health
```

看到下面这些才算好：

```
"status":"ok"  "auto_analysis_ready":true  "hexrays_ready":true
"idb_path":"...Cybersole.exe.i64"  "imagebase":"0x140000000"
```

正常耗时：点完第 2 个框到端口起来约 **10–20 秒**；`ws` 会涨到 **1.9 GB**（库已载入）。

## 四、踩过的坑

| 现象 | 真实原因 | 处置 |
|---|---|---|
| `PROXY: MISSING` + 端口拒绝 | DSH 没拉起 `python -m ida_pro_mcp` | **无关紧要**：`analysis/ida.py` 直连插件，不需要代理 |
| `TIMEOUT: no listener after 180s` | 模态框没点 | 见第二节 |
| IDA 进程在但端口全关 | 同上 | 同上 |

## 五、这个 IDB 的一个硬事实（R691 实测）

- 假数据集区域 `0x143600000..0x143800000`：**代码 xref 0 个**（512 页全探）
- 该区域在 `.rdata`(58 MB) + `.data`(11 MB) 里的**指针 0 个**（原生 `bin_search` 扫过）
- 任何字符串字面量、包括 locale 那个大 JSON blob：**xref 0 个**

**这是 NativeAOT 的寻址形态**：字面量与数据在冻结堆里，靠指针数组/相对偏移访问，
IDA 不把它建模为指针。**所以「字符串 → xref → 函数」这条路在原版上根本不通**，
不能用它找「谁发出了这条文案」。
