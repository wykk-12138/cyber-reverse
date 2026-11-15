import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 控制器族普查：又短了一截，而且池子会「粘」字（第 126 轮）

用「记全了吗」去查控制器族，得出两件事。

### 一、表又短了 —— 这次找到 5 个

```
Cart-UpdateProduct            Cart-ShowLayer
Adyen-PaymentFromComponent    Adyen-PayPalPatchOrder    Adyen-Authorize3DS2
```

这已经是**第三次**同型遗漏（R117 `CheckoutServices-SubmitBilling`、R125
`Adyen-SaveExpressShopperDetails`、R126 这五个）。

> **「表是窗口读出来的」不是运气问题，是方法问题。** 只要还是「读一段就记下来」，
> 就会继续短。这一轮之后控制器词表 **33 条**。

### 二、池子里的名字会带「粘连尾巴」

裸扫 `Prefix-Name` 得到 **94 个**「控制器」，但里面大量是粘连变体：

```
Cart-AddProduct      ←→  Cart-AddProducton
Cart-MiniCartShow    ←→  Cart-MiniCartSh92000052on
Cart-AP              ←→  Cart-APon / Cart-APs
Cart-EditProductLineItem ←→ Cart-EditProductLineIteon
```

原因：**池子里字符串和元数据交错存放**，一个真名字后面可能紧跟着别的字节，
拼出来就是「真名 + on」「真名 + 92000052」这种尾巴。

所以真实数量接近 33，不是 94。**过滤规则是「尾巴得像个方法名的词」—— 这是判断，不是测量**，
代码里标成判断（`TheTableKeepsNoMangledNames` 断言这些粘连变体**不在**词表里）。

### 三、顺手修的一个测试坏习惯

我原本写 `Assert.Equal("CheckoutServices", families[0].Key)` —— **凭记忆指定「最大的族」**。
实测 `CheckoutServices` 是 7 条，而它并不是最多的那个。

这已经是**第五次**在断言里手写数字/名字。改成结构化断言：

```csharp
var biggest = families[0].Count();
Assert.Equal(families.Max(f => f.Count()), biggest);   // 最大的确实是最大的
foreach (var needed in new[] { "CheckoutServices", "Adyen", "Cart" }) …
```

> **测试里不要写「我认为答案是多少」，要写「答案和它的来源一致」。**
'''

if "## 控制器族普查" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("census documented")
else:
    print("already present")
