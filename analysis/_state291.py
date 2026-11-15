import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 291 轮：**文案审计** —— 21 个"缺失键"全是改名或截断，没有真缺口

### 一、为什么查这个

一直有个没验过的担心：复刻件的界面文案是不是漏了原版的一部分。
池子里有 **2007** 个"键形状"的字符串，复刻件 en 有 **1142** 个键 —— 数字差得多，值得查清。

### 二、方法（把噪音挡在外面）

只比**复刻件自己也有的顶层组**（58 个），避免把 `Acornima.Properties.*`、`ADVAPI32.dll`
这类库名/文件名算成"缺失文案"：

```
复刻件顶层组 58
落在这些组里的池子键 1006
其中复刻件没有的     21
```

### 三、21 个逐个看：**没有一个是真漏的**

| 类型 | 例子 | 判定 |
|---|---|---|
| **截断** | `CaptchaSource.Na`（真身 `CaptchaSource.Name.*`）、`SmartActions.Res`（应是 `Resources`） | 解析产物 |
| **组名不是叶子** | `Tasks.LinkChange`、`Tasks.Quicktask` —— 池子里还有 `.InvalidMessage/.InvalidTitle`，复刻件**两者都有** | 非缺失 |
| **改名** | `Proxies.Add` ↔ `Proxies.Action.Add`；`Tasks.Clone` ↔ `Tasks.Context.Clone`；`Tasks.StartAll` ↔ `Tasks.Action.Start`；`Tasks.New` ↔ `Tasks.Action.Creator` | 同一批动作、不同键名 |
| **噪音** | `Update.exe` | 文件名 |

复刻件 `Tasks.*` 有 40 个键，风格是 `Tasks.Action.Start` / `Tasks.Context.Stop`；
原版是扁平的 `Tasks.StartAll` / `Tasks.StopAll`。**两套命名，覆盖同一批动作。**

### 四、诚实标注

"改名"这个判定是**按名字相似度**做的，**没有拿值去比**（池子里键与值不相邻）。
所以准确说法是：**没有发现文案缺口，而不是证明了文案完全一致。**

### 五、这一轮没有改代码

### 六、这一轮的一句话

> 2007 vs 1142 这个差距看着吓人，查完发现是**命名风格不同**，不是漏了大半界面。

> **吓人的数字常常只是口径不同 —— 但只有查过的人有资格这么说。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 291 轮（文案审计：池子 2007 键 vs 复刻件 1142 键，21 个"缺失"全是改名/截断，**无真缺口**）。

---

## 文案审计结论

| 数字 | 值 |
|---|---|
| 池子"键形状"字符串 | 2007 |
| 复刻件 en 键 | 1142 |
| 落在复刻件自己 58 个顶层组里的池子键 | 1006 |
| 其中复刻件没有的 | **21** |
| 判定为真缺口的 | **0** |

21 个分四类：截断（`CaptchaSource.Na`、`SmartActions.Res`）、组名非叶子（`Tasks.LinkChange`）、
**改名**（`Proxies.Add`↔`Proxies.Action.Add`、`Tasks.StartAll`↔`Tasks.Action.Start`）、噪音（`Update.exe`）。

**诚实标注**：改名是**按名字**判的，没比值（池里键值不相邻）→ 结论是"没发现缺口"，不是"证明一致"。

## 验证状态（未改代码）

```
完整套件 1443 通过 / 0 失败 / 2 跳过（R290）
mutation 24/24 fired（R286）
Commit 16.4 GB / 可用 18.78 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
