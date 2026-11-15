import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 两条写在代码里的细节：装在**原型**上，`languages` 只有**一个**（第 164 轮）

原版这两行不是散文，是规格：

```js
Object.keys(NAV).forEach((key) => value(Navigator.prototype, key, NAV[key]));
value(Navigator.prototype, 'languages', Object.freeze([NAV.language]));
```

### 一、装在原型上

第一行说**位置**：属性装 `Navigator.prototype`，不是实例 —— 检测器可以读
`Object.getOwnPropertyNames(navigator)` 看它们是不是「自己的」。

### 二、`languages` 是一个元素

第二行说**数量**：一个语言，且冻结。手机报 `["nl-NL"]`，桌面才报 `["nl-NL","en-US"]`。

### 三、实测纠正：`defineProperty` 可能「接受但无效」

第一版只往原型上装，结果：

```
platform 仍是 Win32，languages 却是 1
```

同一个 `put` 里有的生效有的不生效 —— **`defineProperty` 不抛异常，不代表读回来是那个值**。
改成「原型、实例都试，**用读回值验证**」：

```js
const targets = [P, N];
for (…) { try { Object.defineProperty(target, name, {...}); if (N[name] === v) return; } catch (e) {} }
```

真浏览器最终读回：

```
["nl-NL",1,"nl-NL",true,"iPhone","Apple Computer, Inc.","20030107"]
```

### 四、守卫自己的 bug

`JsGuard` 忽然报 `braces: unbalanced: 2` —— 因为注释里那句
`browser's own accessor may answer…` 的**撇号**被当成字符串开头，把后面整段代码吞了。
改成**先跳过注释、再处理引号**。

> **一个会算错的守卫比没有守卫更坏 —— 它会让正确的代码变红。**

### 五、这一轮的一句话

> 两行代码，两个规格：**位置**和**数量**。我按字面实现位置，被浏览器的行为纠正；
> 按字面实现数量，一次就对了。
>
> **照着规格写，还要照着现实验。规格说「装上去」，现实说「装上去不等于读得到」。**
'''

if "## 两条写在代码里的细节" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("placement documented")
else:
    print("already present")
