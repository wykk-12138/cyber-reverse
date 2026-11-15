import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R351：Group Settings —— 把「Group Name」搬到 tab 之上，页脚改成 Delete / Save

### 实机（R350 读数）

```
Group Settings                                  [×]
Group Name [Group 1]                  ← tab 之上、独立一行
 Delays | Limits | Captcha | Notifications
[ Delete ]                    [ Save ]     ← 底部两键，Delete 红
```

### 复刻件改了什么

1. 顶部加 `Group Settings` 标题 + **`Group Name` 独立行**（`groupName` 绑定 `_group.Name`）；
2. `General` tab 里**删掉 `Name` 那一行**（避免两个编辑器改同一个值），只留 `Pinned` / `Order`；
3. 页脚 `Save / Reset` → **`Delete` / `Save`**，并新增 `DeleteGroup()`（从 `Config.TaskGroups` 移除并保存，
   返回是否真的删到）。

### 还没改的（证据不足）

- `Delays` 的 🔗 联动、`Limits` / `Captcha` / `Notifications` 三个 tab 的内容（实机尚未逐个读完）；
- `Pinned` / `Order` / `Manual` tab 里的 `PeriodStart`：实机 4 个 tab 里没有它们的位置。

**tab 数仍是 6**，这是已知差异，等三个 tab 读完一次性收敛。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 351 轮：Group Settings 的「名字在 tab 之上」落地，页脚改成 Delete/Save

### 一、照实机改了三处

1. 顶部 `Group Settings` 标题 + **`Group Name` 独立行**；
2. `General` tab 里的 `Name` 行**删除** —— 避免两个编辑器改同一个值（这类重复我以前犯过）；
3. 页脚 `Save/Reset` → **`Delete/Save`**，新增 `DeleteGroup()`（移出配置、保存、返回是否真的删到）。

### 二、四次编译失败的教训

这一轮又在一个长方法上做局部替换，连续四次编译不过（`danger:` 参数不存在、`Delete` 方法名、
`FontWeight` 要用类型名、`name` 变量被我删了但还有一行用它）。
**每次都是"改了 A 没看 B"** —— 和 R340 同一个病。

> 结论还是那句：**长文件里改结构，直接替换整个方法/整段，不要逐行拼接。**

### 三、验证

```
完整套件   1515 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> tab 数还是 6（实机 4），`Pinned/Order/PeriodStart` 仍无家 —— 但**"名字在 tab 之上"这条已按实机落地**。

> **一次只收敛一条已证实的差异，比一次改完再返工快。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 351 轮（Group Settings：`Group Name` 移到 tab 之上、页脚改 `Delete/Save`）。

---

## Group Settings 现状（`TaskGroupView`）

| 项 | 实机 | 复刻件 |
|---|---|---|
| `Group Name` | tab 之上的独立行 | **已同（R351）** |
| 页脚 | `Delete`(红) / `Save` | **已同（R351）** |
| tab 数 | 4（Delays/Limits/Captcha/Notifications） | 仍是 6（多 `General` / `Manual`） |
| `Pinned`/`Order`/`PeriodStart` | 未找到位置 | 仍在 `General` / `Manual` |

**下轮**：把实机 `Limits` / `Captcha` / `Notifications` 三个 tab 的内容读全，再一次性收敛 tab 数。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
