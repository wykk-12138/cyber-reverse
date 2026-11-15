import io
p = r"D:\projects\cyber-reverse\docs\HANDOFF.md"
t = io.open(p, encoding='utf-8').read()

# 1) .NET 8 -> .NET 10 (two spots) and net8 reference
t = t.replace('把 Cybersole.exe **5.18.32**（.NET 8 **NativeAOT**，无 IL）在 replica\\ 里做成**功能 1:1** 的复刻件：',
              '把 Cybersole.exe **5.18.32**（**.NET 10 NativeAOT**，无 IL）在 replica\\ 里做成**功能 1:1** 的复刻件：')
t = t.replace('（.NET 8 **NativeAOT**，无 IL）', '（**.NET 10 NativeAOT**，无 IL）')
t = t.replace('复刻件：.NET 8 + Avalonia 11.3.2 + xunit', '复刻件：.NET 8 + Avalonia 11.3.2 + xunit（目标框架不必跟随原版）')

# 2) insert an exe-reverse / triage-diff section right before "## 四、红线"
anchor = '## 四、红线（违反会静默污染结论）'
add = '''## 三·补、只读读数器（不用加载 skill）

`exe-reverse` 已**停用 skill 注册**（仓库仍在 `D:\\projects\\exe-reverse`，junction 在 `.dsh\\skills-disabled\\`），
原因：它的交付判据是"打补丁后仍能运行"，与"忠实重实现"方向相反，容易被误当方法论主导。
**只保留两个只读脚本，绝对路径直调**：

```
python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_triage.py <exe>
python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_diff.py   <exeA> <exeB>
```

已经用它们得到的事实（别再重复试）：
- 原版是 **.NET 10**（PDB 路径 `bin/Release/net10.0/win-x64/native/Cybersole.pdb`，linker 14.44）；
- 39 个导出**全是 Brotli**（`BrotliDecoderDecompress` 等），不是应用符号 → "导出表当符号源"这条路断了；
- **TLS callback 存在**（`0x3105edc`）→ 断点打 `AddressOfEntryPoint` 太晚；
- 5.18.32 ↔ 5.18.35：6 个节全部重排、4.19 MB 字节差异 → 版本 diff 只能在 inventory/资源/字符串层面做。

'''
assert anchor in t
t = t.replace(anchor, add + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('HANDOFF.md updated')

p2 = r"D:\projects\cyber-reverse\docs\GOAL.md"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '### 已知可用来交叉验证的两组输入'
add2 = '''### 什么时候用只读读数器（不加载 skill）

| 需求 | 命令 |
|---|---|
| 新二进制/新版本先分诊（20 秒，纯只读） | `python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_triage.py <exe>` |
| 两版之间节/资源层面变了什么 | `python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_diff.py <A> <B>` |

`exe-reverse` 的 **skill 注册已停用**（`.dsh\\skills-disabled\\`）：它的框架是"打补丁让程序还能跑"，与本任务相反；
脚本可用，框架不采用。

'''
assert anchor2 in t2
t2 = t2.replace(anchor2, add2 + anchor2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('GOAL.md updated')
