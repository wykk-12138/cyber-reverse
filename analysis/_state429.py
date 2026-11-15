import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 429 轮：工作区应当从原版安装目录挪走；顺手发现原版已经自更新到 5.18.35

### 一、为什么必须挪

当前会话的根是 `C:\\Users\\wykk\\AppData\\Local\\Cybersole` —— 那是 **Velopack 的安装/更新目录**
（`current/` + `packages/` + `Update.exe`）。会话以它为根，任何相对路径写入都可能落进原版目录，
而 AGENTS.md §2.3 明令那里**只读**。

### 二、它今天还变过一次

```
16:07:18  packages/Cybersole-5.18.35-win-x64-full.nupkg
16:07:19  current/Cybersole.exe                 123.32 MB
16:07:20  Cybersole.exe (stub) / sq.version
```

原版**自更新到 5.18.35**。以它为根，工作区本身是个移动目标。

**污染的排除**：今天被改的文件全部是原版更新产物，时间戳同一批（16:07:18–20），不是我写的；
我这一程只写 `D:\\projects\\cyber-reverse` 与 `%APPDATA%\\CybersoleReplica`。

### 三、两个版本的事实

| 版本 | 路径 | 大小 | SHA256 前 16 |
|---|---|---|---|
| **5.18.32**（任务目标，IDB 基于它） | `target\\Cybersole.exe` | 123.26 MB | `F2B96D9ABD76559C` |
| 5.18.35（今天更新的） | `Local\\Cybersole\\current\\Cybersole.exe` | 123.32 MB | `0D98E405E0620AA9` |

**已把 5.18.35 复制到 `target-alt\\Cybersole-5.18.35.exe`**（哈希一致），防止下一次更新覆盖掉。
它是 REA `compare_application_versions` / `compare_functions` 的天然输入 —— 两个只差三个小版本的同一程序，
正好用来检验"我们的成员推断对不对"。

### 四、交付

- `docs/HANDOFF.md`：新会话用的**一段话交接提示词** + 挪工作区的理由 + 两版本事实表；
- `target-alt/Cybersole-5.18.35.exe`：第二参照，只读。

### 五、这一轮的一句话

> 我原以为这轮只是"要不要换目录"，结果查出一个**参照物漂移**：目标 5.18.32 没变，但机器上的原版已经 5.18.35。

> **核对工作区的同时顺手核对输入，才发现输入也会自己动。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('## 数据目录', '''## 参照物（两个版本，别混）

| 版本 | 路径 | 用途 |
|---|---|---|
| **5.18.32** | `target/Cybersole.exe`（IDB 基于它） | **任务目标** |
| 5.18.35 | `target-alt/Cybersole-5.18.35.exe`（原版今天自更新出来的，已存档） | 只作对照输入（REA `compare_application_versions`） |

## 数据目录''', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
