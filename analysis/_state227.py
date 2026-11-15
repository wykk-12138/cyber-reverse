import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 227 轮（TaskView 四个绑定名转为 public、新增 Next/PreviousGroup 与 SetQuery；CopyUrl 因缺前置条件撤掉；缺口 105；1419 绿）。

---

## 下一步的第一件事：给 store 补 URL

`CopyUrl` 的证据链是完整的，但**卡在复刻件缺一环**：

```
原版：Models.Store 绑定 Url；Models.BotTask 绑定 Product/Products（无 Url）；TaskView 绑定 CopyUrl
复刻件：IStoreModule 没有 Url，StoreRegistry 只有 Modules
```

→ 要做 `CopyUrl`，先给 `IStoreModule` / store 注册表补 `Url`，再复制 `store.Url + 商品路径`。
**没有这一步，任何 CopyUrl 实现都是编语义。**

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
