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

| 3 | `Load PDB file`（**仅复刻件实例**） | `The input file was linked with debug information stored here` | **Yes**（`Load types`+`Load names` 保持勾选） | 符号名是 C10 与所有覆盖率度量的基础；点 No 等于放弃符号 |

**第三类框只在复刻件产物上出现**（原版 `.i64` 无 PDB）。漏掉它的表现是：进程在、`ws` 不动、**CPU 25 分钟只用 9.6 秒** —— 看起来像在分析，其实在等。

### 三半、端口开 ≠ 分析完

```
python analysis/wait_ready.py 13338 1500
```

轮询 `server_health.auto_analysis_ready`。**不要用端口判断**：插件一加载就应答，而自动分析还在跑。
55 MB AOT 实测 **320 秒**。端口一起就导出的后果见 `BLOCKERS.md` §127（得出 9/819 的中间值）。

**历史记录在** `docs/PARITY_PRODUCT.md` §8「踩过的坑（R433）」：那次是 136,798 → 187,328，
比值 **0.730**；R694 是 136,989 → 187,732，比值**同样 0.730**。
**两处说的是同一个中间态** —— 本清单是操作入口，那边是原始记录。
**注意那边的判据「窗口标题不带 Loading + 连续两次取值相同」已被本清单的 `auto_analysis_ready` 取代**：
稳定性意味着两次一致性不能证明正确（见 `analysis/wait_ready.py` 文件头）。


### R707 补充：第一个框的答案**取决于二进制有没有变**

R691 那份只写了「选 **Load existing**」。那是**二进制未变**时的正确选择。
本轮换了新产物（55,080,448 → 55,349,248 B）再开 IDA，正确的选择是 **覆盖(O)** ——
加载旧库等于拿旧字节的语义去解释新产物。

| 情形 | 选什么 |
|---|---|
| 二进制**没变**，只想恢复上次的分析 | **加载现有(L)** |
| 二进制**变了**（重建过、换过源码） | **覆盖(O)**，让 IDA 重新分析 |

**判断依据**：`Cybersole.Ui.exe` 的字节数/修改时间是否与开库时那只一致。
本轮实测：覆盖后 `ws` 322→567 MB，随后弹「加载新文件」，确定后 CPU 3→8.8 s，再弹 PDB 框，
选「是」后 CPU 8.8→51.2 s，约 **400 秒**后 `auto_analysis_ready: true`。

**另一个坑（本轮踩到）**：`analysis/wait_ready.py` 把「连接被拒」当致命错误，直接退出。
而插件在分析后段才绑端口，所以**前几分钟必然是连接被拒**。
改用 `python analysis/poll_ready.py <port> <timeout> <pid>`：它容忍拒绝，并打印 **CPU 增量**——
本轮那个增量稳定在 ~9.6 s/10 s，是判断「在算」还是「卡在框里」的唯一可靠信号。
