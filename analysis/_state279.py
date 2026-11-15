import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 279 轮（`FlowArtifactTests` 三条不变量；**两条当场打掉我的假设**并已改正）。

---

## 两个被实测推翻的假设（记住，别再犯）

| 假设 | 实测 |
|---|---|
| 保守版 B 是宽版 B 的 **base 子集** | **不是** —— 不同的 `min_rows` 让同一组的 base 地址不同（`wide 129 / conservative 39`，无一同 base） |
| 序号 ≥ 200 的"只是零星几个" | **39 / 320 ≈ 12%** |

**所以**：`FlowArtifactTests` 现在只测**形状**（base 非空、每组 ≥2 步、名字非空、A 布局 69 段/320 步），
大序号只设上限 80 作防洪，不声称"罕见"。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；此后子集）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.28 GB / 可用 7.27 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
