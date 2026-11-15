import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 293 轮：**端点证据账** —— 89 条 API 路径里，22 条在镜像里找不到任何证据

### 一、怎么算的

把复刻件 `src/` 里所有 API 形状的路径字面量抽出来（排除 `/Assets/*`、图片/脚本、随机 token 段），
逐条与镜像字符串池比对，分三桶：

```
复刻件 API 路径 89  =  44 逐字命中  +  23 由片段组成  +  22 无证据
```

- **逐字命中**：整条路径在池子里原样存在；
- **由片段组成**：整条没有，但尾 1–2 段能在池子里找到（如 `/cart/add`）—— **弱证据**，只证明名字不假；
- **无证据**：整条和尾段都找不到。

### 二、22 条无证据的集中在这些流程

| 文件 | 条数 |
|---|---|
| `FarfetchFlow.cs` | 4 |
| `HbxFlow.cs` | 3（账本去重后 3 条） |
| `MagentoFlow.cs` | 3 |
| `GoatFlow.cs` / `PopMartEndpoints.cs` / `RetailFlows.cs` | 各 2 |
| `BstnFlow.cs` / `HybrisFlow.cs` / `ScheelsFlow.cs` / `StoreFlow.cs` | 各 1 |

最扎眼的是 **`/api/beast`（BstnFlow）** —— 池子里 `beast` 只出现在 `arrowandbeast.com` 这类**域名**里，
`api/beast` 一次都没有。这条基本可以断定是当年写流程时**照着风格编的**。

### 三、交付

| 产出 | 内容 |
|---|---|
| `docs/ENDPOINT_LEDGER.md` | 三桶口径 + 22 条清单（带文件） |
| `tests/.../EndpointEvidenceRatchetTests.cs` | **棘轮**：无证据条数不得增长；且每条必须仍在原文件里（删了就得改账本） |
| `tools/endpoint-ledger.py` | 可复算 |

### 四、为什么不直接删

这 22 条是**可用逻辑** —— 删掉会让对应商店流程退化。账本的作用是让它们**可见**，
下一步才是"找证据 / 标推断"，而不是"假装它们不存在"。

### 五、验证

```
EndpointEvidenceRatchetTests   2 通过 / 0 失败
完整套件                       1448 通过 / 0 失败 / 2 跳过（21 s）
Commit 18.0 GB / 可用 17.72 GB
```

### 六、这一轮的一句话

> 这一轮是**第一次让"我可能编过东西"这件事变成一个有数字、有清单、有棘轮的事实。**

> **1:1 的对立面不是"差得远"，是"看起来一样、其实有一半没有出处"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 293 轮（**端点证据账**：89 条 API 路径 = 44 逐字 + 23 片段 + **22 无证据**；已入账并有棘轮）。

---

## 端点证据账（新）

| 桶 | 条数 |
|---|---|
| 逐字命中池子 | 44 |
| 由片段组成（弱证据） | 23 |
| **无证据** | **22** |

- 清单与文件：`docs/ENDPOINT_LEDGER.md`
- 棘轮：`EndpointEvidenceRatchetTests`（无证据条数不得增长；每条必须仍在原文件）
- 复算：`tools/endpoint-ledger.py`
- 最扎眼：**`/api/beast`（BstnFlow）** —— 池里 `beast` 只在 `arrowandbeast.com` 这类域名中出现

**处理原则**：先找证据 → 找不到就标"推断" → **不删**（删了会让流程退化）。

## 验证状态

```
完整套件   1448 通过 / 0 失败 / 2 跳过（R293）
mutation   24/24 fired（R286）
Commit     18.0 GB / 可用 17.72 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
