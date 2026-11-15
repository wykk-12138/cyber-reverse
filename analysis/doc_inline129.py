import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 常量干净不等于代码干净：**202 条内联字面量里 29 条不在镜像里**（第 129 轮）

第 128 轮的闸门只查 `public const string`，报「159/159 逐字命中」。这一轮把范围扩到
**方法体里的内联字面量**，结果立刻不一样：

```
endpoint constants:            160     verbatim in pool: 160    invented: 0
inline URL/path literals:      202     not in pool: 29
```

### 一、当场抓到一条：Nike 的下单

`NikeFlow.SubmitOrderAsync` 里写着

```csharp
$"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/submit"   // ← R87 的发明，一直在代码里
```

**常量扫描看不见它**，因为它不是常量。R127 找到的 `NikeEndpoints.OrderV5` 才是镜像里那条。
现在改成 POST `OrderV5`，cartId 放 body（路径里没有位置放它）。

### 二、三类溯源，缺一不可

| 类 | 含义 | 例子 |
|---|---|---|
| `literal` | 逐字出现在镜像里 | `OrderV5`、`bff/v2/orders` |
| `live` | 镜像里没有，但**真实响应过** | BSTN `/api/beast`（R91 实测该前缀会应答） |
| `fixture` | **故意保留的不存在路径**，用测试禁止 | Pop Mart `/api/cart/add` 等三条（R100） |

「三者都不是」= 发明。台账写在 `docs/ENDPOINT_PROVENANCE.md`。

### 三、闸门改成「不许增长」而不是「必须为零」

剩下 **24 条待定**（Farfetch、Goat、HBX、Hybris、Magento、RetailFlows、Scheels、StoreFlow 等）。
一条条查清要好几轮，所以第 8 步的门槛是：

```
unknown (invented and unregistered): 24   baseline: 24     → PASS
超过 baseline → exit 1
```

**这是棘轮：只许往下走。** 每轮清掉几条就把 baseline 调低。

### 四、为什么不用「必须为零」

如果现在就把门槛设成 0，第 8 步永远是红的 —— **一条永远红的检查等于没有检查**
（这正是 R108 那轮「整轮跑不完」的教训）。棘轮能保证「不再变坏」，同时留下可见的清单。

### 五、这一轮的一句话

> 上一轮我以为闸门做完了，因为常量 159/159 干净。
> 这一轮把范围一扩，**29 条不在镜像里，其中一条正是我自己在 42 轮前编的 Nike 下单路径。**
>
> **「我检查过了」这句话，永远要跟着「我检查的是哪一部分」。**
'''

if "## 常量干净不等于代码干净" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("inline scan documented")
else:
    print("already present")
