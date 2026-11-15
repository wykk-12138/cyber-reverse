import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 283 轮（新增**一页接手简报** `docs/RESUME.md`：数字带口径 / 三件待办 / 五项做不了 / 五条纪律）。

---

## 新会话从这里开始：`docs/RESUME.md`

`VERDICT.md` 已 97 万字节、280+ 轮，**不能当入口**。一页简报里有：

- **数字（带口径）**：1442 通过 / 缺口 33 / 不可达 29 / 18 条流水线 / 2 条字面量流；
- **三件待办**：全量 `mutation-check`（24 条，12–15 分钟）→ 全套确认 → 结构性工作；
- **五项做不了**（各附原因）：`Attributes.Platform` 三值 / `OpenRelease` / Shopify 头方向 /
  行控件 5 个 / 段→商店归属 14 条；
- **五条硬纪律**：数字带口径 · ceiling 等于实测值 · 先读那一行 · 用替换不用插入 · 报绿要说口径；
- **内存纪律** + **文件地图**。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation-check 冒烟 5/24 全 fired；全量待重启后跑
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 41.44 GB / 可用 6.13 GB   ← **低于 8 GB 硬线，建议重启**
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
