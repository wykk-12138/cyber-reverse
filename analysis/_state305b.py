import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
old = '''mutation（27 条全量）          见下一段'''
new = '''mutation（27 条全量）          **27/27 全部 guard fired**，restored tree: GREEN'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 305 轮（新增 3 条变异 → **抓出我自己的装饰性守卫**并修好；全量 **27/27 fired**）。

---

## mutation-check 现在是 27 条，全量 27/27 fired

R287–R303 的三条新守卫此前从未被变异检验。补进脚本后：

| 变异 | 首轮结果 | 修好后 |
|---|---|---|
| round 290 流序号 45→44 | fired | fired |
| round 292 错误目录标题改写 | fired | fired |
| **round 294 去掉推断标记** | **DECORATIVE（假守卫）** | **fired** |

### 假在哪

断言原来是"**文件里**出现 `inferred: no image evidence`"，而 GoatFlow 有两处标记 → 删一处仍绿。
改成"**每一行**用到该路径的代码行都要带标记"后，还抓出三处真实漏标
（Farfetch `/payment`、Goat `/v1/buys/{id}` ×2、Bstn `/api/beast/` 的消息字符串）。已补齐。

### 三条纪律（新增）

1. 新守卫写完**立刻**做变异检验；
2. 断言落在"**行**"上，不是"文件"上；
3. 同一个方法多处调用 → 一处标了不等于都用处标了。

## 验证状态

```
全量 mutation   27 / 27 fired     restored tree: GREEN
完整套件        1458 通过 / 0 失败 / 2 跳过
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('docs updated')
