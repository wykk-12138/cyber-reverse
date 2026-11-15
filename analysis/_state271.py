import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 271 轮（段→商店再排除两条路：方法名不含品牌 0/69、复刻件模块无对象可切；边界已写清）。

---

## 段→商店：只剩一条路

| 路 | 结果 |
|---|---|
| 通用动作名指纹 | 27 段命中但不可判 |
| **独有动作名指纹（人工 4 组）** | **9 段绑上**（Shopify 3 / Demandware 4 / Popmart 1 / Nike 0） |
| 方法名含商店名（20 个品牌） | **0 / 69** |
| 段邻近字面量含商店名 | **0 / 69** |
| 复刻件商店模块独有方法 | 无对象可切（模块是数据驱动的，`Stores/` 只有一个抽象文件） |
| **John Lewis 锚点** | **未做 —— 唯一剩下的路** |

**统计**：段内方法名 216 个，其中 172 个（80%）只出现在一段里 →
指纹法上限很高，瓶颈是**我不知道哪个独特名字属于哪家店**；镜像是不会自己说的。

完整边界见 `docs/FLOW_SEQUENCES.md` 第六至九节。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.87 GB / 可用 7.51 GB   ← 未重启，低于 8 GB 硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
