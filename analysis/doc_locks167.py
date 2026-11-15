import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 十三里装两个，并且**装的顺序**本身就是正确性（第 167 轮）

`standalone`（布尔）与 `locks`（Web Locks API）都能不靠模拟就说得通：调 `request` 的页面要的是**回调跑起来**，
不是真的排队。两者都装 `Navigator.prototype`（R164 的规矩），都进 `MaskTargets`（R160 的规矩）。

```
locks.request(name, callback)   length 2   回调执行，返回 Promise
locks.query()                   length 0   空快照 { held: [], pending: [], granted: [] }
```

### 一、实测

```
probe  = [false,"object","function",2,"function",0]
ran    = true:true      // Promise 已返回，回调已跑
masked = ["function get locks() { [native code] }", "function request() { [native code] }"]
```

### 二、装的位置错了，顺序就崩了

第一版把这两个**装在 reseat 之后**，于是它们落到原型属性列表的末尾 —— 实测：

```
recorded names present on the prototype: 29/50
relative order preserved: False
```

把安装移到 reseat **之前**，两条同时成立：29/50、相对顺序 True。

> **每一次「安装一个成员」都会在原型末尾追加一项。所以任何重排都必须排在所有安装之后。**

这条不是风格问题，是**顺序即正确性**——与 R161 里「mask 必须最后跑」是同一条规律。

### 三、这一轮的一句话

> 上一轮我说「先不装和忘了装是两件事」。这一轮装了，立刻撞到第二件事：
> **装的时机，和装不装一样重要。**
>
> **一个 pass 链条里，每一步的位置都是它语义的一部分。**
'''

if "## 十三里装两个" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("locks documented")
else:
    print("already present")
