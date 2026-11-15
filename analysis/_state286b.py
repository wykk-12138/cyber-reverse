import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 286 轮（重启后）：**全量 mutation-check 24/24 全部 fired** —— 一笔挂了 66 轮的债清了

### 一、重启后的机器

```
开机 23:19:35     Commit 12.62 GB（峰值 12.62）     可用物理 20.65 GB
```

### 二、全量 mutation-check（上次跑是 R220）

```
running 24 of 24 mutations
  [guard fired] × 24        没有一条 skip、没有一条 "decorative"
restored tree: GREEN
```

**24 条逐条列出（每条都真的让对应守卫变红）**：

| round | 变异点 |
|---|---|
| 136 ×3 | `contentWindow` 重放 / `createElement` 重放 / 裸全局重放新 realm |
| 137 | `speechSynthesis` 语音列表 |
| 138 | 只读一个版本号 |
| **127** | **Flush 先出队再判 sink**（R284 修过锚点，本轮**第一次真的跑起来**） |
| 133 | locale 字典丢掉 `WithCulture=false` |
| 124 ×3 | catch 消息被下一行覆盖 / 新造一个死按钮 / `Config.Save` 旁的丢弃对象 |
| 122 | 跨层 await 丢 `ConfigureAwait` |
| 112 | 注释里写入 mojibake |
| 134 ×3 | 引擎资源不再嵌入 / geetest 载 v4 / reCAPTCHA 页不载脚本 |
| 135 ×2 | screen 表与 geometry 表不一致 / 设备表少一个声明 |
| **164 ×2** | **PARITY.md 模块计数 / UI 计数漂移**（R284 修过锚点，本轮**第一次真的跑起来**） |
| 168 / 169 | locale 键重复 / locale 丢键 |
| 179 | 事件声明、raise、没人订阅 |
| 187 | Cloudflare provider 只加进两个列表之一 |
| 10 | 空白 shipping preference 不再被处理 |

> **R284 那两条哑掉的护栏（127 / 164-UI）本轮都 fired** —— 修锚点不是纸面功夫。

### 三、随后全套

```
快测 Speed!=Slow      1442 通过 / 0 失败 / 2 跳过（20 s）
残留                  chrome 0 / 临时 profile 0
Commit 13.52 GB / 可用 20.42 GB
```

### 四、这一轮的一句话

> 从 R220 到 R285，这条债挂了六十多轮，中间我还一直以为它是 23 条（实际 24）。

> **"跑过"和"知道它现在真能跑"，是两件事** —— 后者需要重启、需要修锚点、需要一次 24 行全绿。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 286 轮（重启后）——**全量 mutation-check 24/24 全 fired、restored GREEN**；全套 1442 绿。

---

## 验证状态：**两笔债都清了**

```
全量 mutation-check   24 / 24 guard fired（0 skip、0 decorative）   restored tree: GREEN
完整套件              1442 通过 / 0 失败 / 2 跳过（20 s）
残留                  chrome 0 / 临时 profile 0
Commit 13.52 GB / 可用 20.42 GB（开机 23:19:35）
```

**R284 修的两条哑护栏（round 127、round 164-UI）本轮第一次真的 fired。**

## 接下来按顺序做

1. ~~全量 mutation-check~~ ✅
2. ~~全套确认~~ ✅
3. **结构性工作**：按 `docs/BINDING_BACKLOG.md` 的 B 类 31 个，先抽行控件
   （`FilterRow` / `ProfileCsvRow` / `ActionRow`）—— 这是缺口里最后一块真活。

## 仍记着的口径

| 指标 | 值 |
|---|---|
| 缺口 | 33（real = ceiling = 账本标题） |
| 不可达 UI 类 | 29 |
| 流水线 | 18 条 / 141 步（2 条字面量） |
| mutation 护栏 | 24 条，全活 |

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
