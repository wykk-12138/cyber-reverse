import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 330 轮（实机结掉 R77 悬案：Payment 的 `Max Open` 是**条件行**；全套 1480 绿）。

---

## 这一轮：实机把悬案问完了

| 状态（原版 5.18.32） | 实机所见 |
|---|---|
| `Auto Open 3DS [No]` | 只有这一行 |
| 切成 `Yes` | 其下**出现** `Max Open [5]` |
| 切回 `No` | **消失** |

→ **`Max Open` 依赖 `Auto Open 3DS == Yes`**（原版已恢复为 No）。复刻件改为条件显示。

**两个测试坑**：未挂载控件没有视觉树（要用逻辑树）；隐藏行仍持有文本块（可见性要看祖先）。

## 状态

```
完整套件   1480 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.3 GB / 可用 17.9 GB
原版进程   pid 14248（Settings → Payment 页仍开着）
```

## 下一步候选（原版还开着，GUI 交叉验证正当时）

1. Tasks 页：列头顺序与工具条按钮（`TaskView` 的 29 个绑定名）；
2. Proxies 页：右键菜单项；
3. Accounts 页：`AccountStoreEntry.IsSelected` 的选中态表现。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
