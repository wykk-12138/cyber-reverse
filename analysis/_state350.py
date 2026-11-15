import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R350：Tasks → 「Group Settings」弹窗 —— 实机 4 个 tab，复刻件 6 个

实机（点 Tasks 页 `Group 1` 旁的齿轮）：

```
[📁] Group Settings                                   [×]
Group Name
[Group 1                                          ]
─────────────────────────────────────────────────
 Delays | Limits | Captcha | Notifications
 Monitor Delay [2500 ms]  🔗   Error Delay [2500 ms]
 Timeout [10 sec]
[ Delete ]                              [ Save ]
```

- `Delays` 的 tooltip：**"Group specific delays. If none are set, global delays will be used, you can adjust these in settings."**
- 🔗 按钮的 tooltip：**"When toggled, both monitor and retry delays will stay the same"**
- 底部两键：`Delete`（红）/ `Save`（绿）

复刻件 `TaskGroupView` 有 **6 个 tab**：`General / Delays / Limits / Captcha / Notifications / Manual`，
而 **`Group Name` 被放在 `General` tab 里**，实机是**放在 tab 之上**。

### 结论：这是结构性差异，本轮**只记录不改**

差异有三处：

1. 实机 **4** 个 tab，复刻件 **6** 个（多 `General` 与 `Manual`）；
2. `Group Name` 的位置不同（实机在 tab 上方）；
3. 复刻件 `General` 里还有 `Pinned` / `Order`，`Manual` 里是 `PeriodStart` —— **实机这三个控件还没找到家**。

**为什么不在这一轮改**：要先把实机的 `Limits` / `Captcha` / `Notifications` 三个 tab 也读一遍，
才能确定 `Pinned` / `Order` / `PeriodStart` 是"另有其处"还是"复刻件多造"。少读三个 tab 就重构，
就是又一次 R340 式的返工。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 350 轮：Group Settings 弹窗 —— 实机 4 个 tab vs 复刻件 6 个（**本轮只记录**）

### 一、实机结构

```
Group Settings                              [×]
Group Name [Group 1]
 Delays | Limits | Captcha | Notifications
 Monitor Delay [2500 ms] 🔗 Error Delay [2500 ms] / Timeout [10 sec]
[ Delete ]                    [ Save ]
```

两条 tooltip 也拿到了（`Delays` 的说明、🔗 的"两个延迟保持相同"）。

### 二、三处结构性差异

1. 实机 **4** 个 tab，复刻件 **6** 个（多 `General`、`Manual`）；
2. `Group Name` 实机在 **tab 之上**，复刻件塞在 `General` tab 里；
3. 复刻件 `General` 的 `Pinned`/`Order`、`Manual` 的 `PeriodStart` —— **实机还没找到位置**。

### 三、为什么这轮不动手

要先读完实机另外三个 tab（`Limits`/`Captcha`/`Notifications`），才能判断那三个控件是"另有其处"
还是"复刻件多造"。**少读三个 tab 就重构 = 又一次 R340 式返工。**

### 四、这一轮的一句话

> 这一轮的产出是一张"待改清单"，不是一行代码。

> **发现结构差异时，先补齐证据再动手 —— 结构改错的代价远高于晚一轮。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 350 轮（实机 Group Settings：4 tab vs 复刻件 6 tab，**只记录待改**）。

---

## 待改：Group Settings 弹窗（证据已录，下轮动手）

| 项 | 实机 | 复刻件 |
|---|---|---|
| tab 数 | **4**（Delays / Limits / Captcha / Notifications） | 6（多 `General` / `Manual`） |
| `Group Name` | **tab 之上的独立字段** | 在 `General` tab 里 |
| `Pinned` / `Order` / `PeriodStart` | 未见 | 在 `General` / `Manual` 里 |

**下轮第一步**：把实机 `Limits` / `Captcha` / `Notifications` 三个 tab 的内容读完，再一次性重构。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
