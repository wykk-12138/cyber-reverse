import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 一个 `reorder`，三个入口，五类规则（第 180 轮）

原版同时改写 `Object.getOwnPropertyNames`、`Object.keys`、`Reflect.ownKeys`，三者都走同一个
`reorder(target, names, enumerableOnly)`。规则有五类：

| 类 | 内容 |
|---|---|
| 全局对象 | 数字索引在前、引擎自身列表居中、本脚本新增的名字在后；`MAIN_FRAME_ONLY`（`_injected_scroll_helper`、`_injected_navigation`）只从**非顶层帧**删除 |
| `CSSStyleDeclaration.prototype` | 用一张录制表回答 —— 「支持的属性列表是最强的引擎指纹之一，两个引擎连接口都不一致」 |
| `CSSStyleDeclaration` **实例** | 只报**数字索引** |
| `ORDER` 表 | `{ match, names, drop }`，`wanted.concat(extra)`；`drop` 用来摘掉设备没有、又删不掉的引擎成员（WebIDL 常量不可配置） |
| Symbol | `OrdinaryOwnPropertyKeys` 把 symbol 放最后，所以字符串部分重排后再把 symbol 接回去 |

### 一、最锋利的一条实测

先把实例过滤到「设备的词汇」，结果 **1505** 个名字 —— 正确的 881 后面跟着 624 个重复：

> a name list that repeats 624 entries is not a vocabulary difference an obscure device could explain; **no engine
> enumerates a property twice**.

原因是 Blink 把 ~1200 个驼峰属性挂在**实例**上，WebKit 挂在 `CSSStyleProperties.prototype` 上，实例只拥有数字索引。

### 二、symbol 那一半

早先的守卫「遇到带 symbol 的对象就跳过」—— 而**每个接口原型都带 `Symbol.toStringTag`**，
于是 `getOwnPropertyNames` 与 `Reflect.ownKeys` 对**同一个对象**给出不同答案：

> which is a sharper tell than whatever the rule was hiding.

### 三、这一轮的实际交付：**建好，但没接线**

`KeyOrderTable` 与它的测试都完成了。接进组合链后，`mutation-check.py` **挂住**：
一条被变异关掉的「重放路由」会因为被包裹的 `Object.getOwnPropertyNames` 而永远等下去。

所以这一轮把那一行**注释掉**，并在 `TheLayerIsBuiltButNotWired` 里断言这个状态：

```csharp
Assert.Contains("// surfaceBody += KeyOrderTable.BodyJs();", bridge);
Assert.Contains("deliberately NOT WIRED", bridge);
```

顺带记录 Blink 的基线（未接线时的真实取值）：

```
sources           = [3,3]        （cloak 之后原生源码都是三行）
css non-numeric   = 750:751      （实例带着 750 个驼峰名 + 1 个数字索引）
```

**这两个数就是接线后要改掉的差距。**

### 四、这一轮的一句话

> 我把「规则读懂了」当成「可以接线了」，实测告诉我还差一步：**被包裹的基础设施会改变别人的失败方式**。
>
> **一个会让工装挂起的正确实现，比一个没接线的正确实现更糟。**
'''

if "## 一个 `reorder`，三个入口，五类规则" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("key order documented")
else:
    print("already present")
