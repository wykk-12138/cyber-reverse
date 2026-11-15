import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 288 轮：再验四条流 —— **内容全对，只是序号打印有粘连**，已改标 `Literal`

### 一、先确认"名字是否真的存在"

拿八条流的每个步骤名去池子里找 `d__` 状态机：

```
nike 16/16   popmart 24/24   johnlewis 19/19
demandware-classic 12/12   demandware-dual 15/15   collectplus-app 17/17
```

**全部存在** —— 说明"端点派生"那几条的步骤名不是编出来的。

### 二、再找每条流的字面量行

| 流 | 最佳单行命中 | 地址 |
|---|---|---|
| **popmart** | **24 / 24** | `0x0337b9e5` |
| **demandware-classic** | **12 / 12** | `0x034ac0f3` |
| **demandware-dual** | **15 / 15** | `0x0336f0bd` |
| **collectplus-app** | **17 / 17** | `0x033929ec` |
| nike | 12 / 16（缺 `StartEcomSession/Authorize/GetAccessToken/FindVariant`） | — |
| johnlewis | 17 / 19（缺 `FindProduct/AddToCart`，正是 R112 用 lambda 补的两步） | — |

### 三、四条满命中流的逐条比对：**名字顺序全一致**

| 流 | 名字顺序 | 序号 |
|---|---|---|
| popmart | 一致 | 差异只是粘连（`1040→104`、`1204→120`、`1154→115`、`1354→135`、`1380→138`、`1428→142`） |
| demandware-classic | 一致 | `356/360/376` = `35/36/37` 粘连 |
| **demandware-dual** | 一致 | **完全一致** |
| collectplus-app | 一致 | `370→37`、`440→44` 粘连 |

**所以这四条本来就是字面量派生，内容也对** —— 已把 `FlowSource` 改标 `Literal`（共 6 条）。
`nike` / `johnlewis` 保持 `Endpoint`（字面量跨行，需再拆）。

### 四、守卫同步

`StoreFlowSourceTests` 里"Literal 只能是那两条"改成六条（含新顺序断言），
"popmart 在 Endpoint 里"改成 `DoesNotContain("popmart", endpoints)`，并写明 nike/johnlewis 为什么还在。

### 五、验证

```
Stores 编译                    0 错误
StoreFlowSourceTests + 流程测试  14 通过 / 0 失败
完整套件                        1442 通过 / 0 失败 / 2 跳过（22 s）
Commit 15.2 GB / 可用 19.44 GB
```

### 六、这一轮的一句话

> R287 我改正了一条流的**内容**；这一轮证明另外四条流的**内容是对的**，只是我把它们标错了来源。

> **错标来源和错写内容，是两种不同的错 —— 前者会让你不敢信任一条其实正确的数据。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 288 轮（再验四条流：内容全对、名字顺序一致，改标 `Literal` → 共 6 条字面量流）。

---

## 流来源账（现在 6 literal / 2 endpoint）

| 流 | 来源 | 依据 |
|---|---|---|
| structure-token-multi | **Literal** | `0x034b14b8` 15/15 |
| structure-token-single | **Literal** | `0x034b23a5` 12/12（R287 改正过内容） |
| popmart | **Literal** | `0x0337b9e5` 24/24，序号仅粘连 |
| demandware-classic | **Literal** | `0x034ac0f3` 12/12 |
| demandware-dual | **Literal** | `0x0336f0bd` 15/15，**序号也全一致** |
| collectplus-app | **Literal** | `0x033929ec` 17/17 |
| nike | Endpoint | 单行仅 12/16（缺 StartEcomSession/Authorize/GetAccessToken/FindVariant） |
| johnlewis | Endpoint | 单行 17/19（缺 FindProduct/AddToCart，R112 用 lambda 补的） |

**八条流的步骤名在池里全部能找到 `d__` 状态机** —— 没有一个是编的。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1442 通过 / 0 失败 / 2 跳过（R288）
Commit 15.2 GB / 可用 19.44 GB
```

## 下一步

1. `nike` / `johnlewis`：把字面量跨行拼起来（B 布局分组），能拼全就改标 `Literal`；
2. B 类 31 个缺口仍是结构差异。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
