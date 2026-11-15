import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 把「顺序即正确性」变成契约（第 168 轮）

三轮的学费：

| 轮 | 谁插错了位置 | 后果 |
|---|---|---|
| R161 | mask pass 想跑在前面 | 它要伪装的 getter 还没装 |
| R156 | 引擎块跑在旧 patch 之前 | 五个插件被三个覆盖 |
| R167 | `locks` 装在 reseat 之后 | 29/50，相对顺序 `False` |

所以这一轮把顺序**写下来，并且让它在源码里可检查**。

### 一、`SurfaceOrder`：九步，每步带「为什么不能动」

```
1 mask          first: every patch after it registers itself as native
2 engine        unconditional: true for every profile
3 webassembly   gated on an Apple claim
4 mobile        gated on an Apple claim
5 touches       after the mobile figures, same prototype
6 prune         after the engine block, deletes what it installed
7 locks         before the reseat, every install appends
8 reseat        after every install, orders what exists
9 mask-pass     last: an uninstalled getter cannot be masked
```

`SurfaceOrder.Check(bridgeSource)` 返回违规列表；`TheBridgeFollowsTheOrder` 用真实源码跑它。

### 二、两条反向断言：错的必须被抓

- **`AWrongOrderIsRejected`**：把 reseat 放到 locks 之前（R167 的真实错误），断言得到
  `reseat appears before locks`，并把原因一起带出来；
- **`AMissingBodyIsRejected`**：删掉 mask pass 那一行，断言 `mask-pass: marker not found` ——
  **少一步不能静默通过**。

### 三、这一轮的一句话

> 前三轮我每次都在运行时发现顺序错了，然后修好。这一轮改成**在编译后的第一秒就发现**。
>
> **一个错误被修好两次，说明缺的不是手，是尺子；被修好三次，说明缺的是把错误写进契约。**
'''

if "## 把「顺序即正确性」变成契约" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("order contract documented")
else:
    print("already present")
