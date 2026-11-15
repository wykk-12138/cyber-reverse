import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 274 轮（用恢复的段对账 `StoreFlowSteps`：**发现它混着 literal 与 endpoint 两类证据**）。

---

## `StoreFlowSteps` 必须标来源（新纪律）

对账结果：`structure-token-multi` **15/15** 命中恢复段、`structure-token-single` **11/12**；
而 `nike` 2/16、`popmart` 0/24、`johnlewis` 4/19、`demandware-*` 2–3/12、`collectplus` 3/17。

原因不是数据错，是**两类行**：

| 类 | 来源 | 能否与字面量逐条对账 |
|---|---|---|
| `literal` | 直接读自一段字面量 | **能**（structure-token-* 就是这类） |
| `endpoint` | 按端点族叙述出来的行为模型 | **不能**（名字体系不同，如 `StartEcomSession` vs `Start`） |

> **不标来源的"1:1"，是把两种证据混在一起算** —— 比不做对账更危险，因为它有数字。

**下一步（要动代码时）**：给 `StoreFlowSteps.Flow` 加 `Source` 字段（`literal` / `endpoint`），
并让对账测试只对 `literal` 行断言。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.94 GB / 可用 7.44 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
