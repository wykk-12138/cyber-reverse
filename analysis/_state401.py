import io
p = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 401 轮：近似错误队列里的第一条真缺陷（AYCD 的两个按钮）

### 一、工具报了 `Disconnect` vs `disconnected`

相似度 0.91，看着像"大小写问题"，实际是**两件不同的东西**：
复刻件里有状态词 `disconnected`，却没有原版的**动作标签**。

### 二、locale 里的整族

```
Settings.Aycd.ConnectButton       Connect
Settings.Aycd.Disconnect.Action   Disconnect
Settings.Aycd.Disconnect.Message  (长句，含 "AYCD Inbox" / "API")
```

### 三、补的

```csharp
public const string AycdConnectLabel = "Connect";
public const string AycdDisconnectLabel = "Disconnect";
```

并把 IMAP 页的 `Connect` 按钮接到常量（原来写死同字面量，现在有据可依）。

### 四、对工具的认识

`locale_near_miss.py` 报的 21 条里：
- **真缺陷**：像这条一样，是"缺一个动作标签"；
- **假阳性**：像 `" Custom Size"` 与 `1 Custom Size`，是**拼接出来的**字符串；
- **位置未定**：像 `Add Size` 与 `Add Size(s)`，得先确认是哪个按钮。

```
完整套件   1575 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 一个"相似度 0.91"的提示，背后可能是一个真缺失，也可能只是拼接字符串。

> **工具的提示要人去看；看完之后写进队列，而不是直接改。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 401 轮（AYCD 的 `Connect` / `Disconnect` 标签补上并接线；套件 1575）。

---

## 近似错误队列：三分类

| 类别 | 例子 | 处置 |
|---|---|---|
| 真缺陷 | `Disconnect` 缺席（只有状态词 `disconnected`） | ✅ 已补（R401） |
| 拼接字符串造成的假阳性 | `" Custom Size"` vs `1 Custom Size` | 忽略 |
| 位置未定 | `Add Size` vs `Add Size(s)` | 先确认按钮再改 |

## 状态

```
完整套件   1575 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
