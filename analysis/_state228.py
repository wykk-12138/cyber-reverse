import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 下一步的第一件事')
head = '''最后更新：第 228 轮（CopyUrl 恢复：URL 一直在 `Product.Url`，R227 的"没有 URL 源"是误判；1422 绿）。

---

## 一条经验（R227 错 → R228 改）

**"某个成员缺"要往下看一层**：R227 只看 `BotTask` 的绑定（`Product`/`Products`）就判定"没有 URL 源"，
实际 `Product.Url` 一直是模型字段，`TaskEngine` 轮询用的就是它。

`CopyUrl` 现在的语义：`Product.Url` → 回退 store 域名（`IStoreModule.Domains[0]`）→ 都没有则返回 false；
没有剪贴板 sink 时写状态行并返回 false（不假装复制成功）。

'''
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
