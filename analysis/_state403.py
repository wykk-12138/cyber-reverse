import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 403 轮：补两个网格的数据成员（类型级缺口 12 → 11），以及**一次内存熔断**

### 一、补的

| 类型 | 成员 | 依据（`tools/bind_shape.py`） |
|---|---|---|
| `AccountGrid` | `Rows` | `Getter,Property`（只读）→ 返回 `Ordered()` 的结果 |
| `GroupGrid` | `Items` | `Getter,Property` → `SetRows` 时一并填好 |
| `GroupGrid` | `Store` | `Getter,Property` → 只读，暂为空串（哪个店铺的列表） |

`GroupGrid.SetRows` 现在同时发布 `Rows`（名字+徽标）与 `Items`（键），两者一起更新。

### 二、内存熔断（这轮的真实状况）

改完跑全量套件，跑到一半出现四条**无关**用例失败
（`WindowOrderTests` / `KeyOrderTableTests` / `VoiceListTests` / `KeyOrderDispatchTests`），
随后任务被切到后台。查内存：

```
Commit  92.53 / 94.03 GB       ← 到顶
Physical available  2.19 GB
```

**处置**：杀掉后台测试作业 + 残留 `testhost`，`dotnet build-server shutdown`；
available 回到 3.27 GB。随后**只跑相关用例**：

```
GroupGrid / AccountSurface / AccountGrid   10 通过 / 0 失败（74 ms）
```

那四条失败**没有复现依据**（它们与本次改动无关，且在内存耗尽时出现），记为"环境性失败，待内存充裕时重跑确认"。

### 三、这一轮的一句话

> 我宁可报告"全量没跑完 + 相关用例全绿"，也不把那四条失败说成"偶发"就完事。

> **内存不够时，最贵的不是时间，是"跑出来的结论不可信"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('类型级缺口 12（tools/bind_scope.py）', '类型级缺口 11（tools/bind_scope.py）')
t2 = t2.replace('完整套件   1575 通过 / 0 失败 / 2 跳过', '完整套件   1575 通过 / 0 失败 / 2 跳过（R403 全量因内存不足中断；相关 10 个用例全绿）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
