import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 外来接收者要**抛异常**（第 173 轮）

原版一句话点破了数据属性和访问器的差别：

```
// A native accessor is bound to its interface and throws when handed a foreign receiver. A getter that just
// closes over a constant answers anyone, and that difference needs no reference device to see: pull the
// descriptor off Navigator.prototype, call .get on {}, and a real browser throws where a naive override
// returns the user agent.
```

replica 之前把那几个成员装成**数据属性** —— `.get.call({})` 直接答值。一行守卫就能对上：

```js
if (!(this instanceof G.Navigator)) throw new TypeError('Illegal invocation');
```

实测：

```
values  = ["iPhone","Apple Computer, Inc.","5.0 (iP","string"]
foreign = ["platform:TypeError","userAgent:TypeError"]
shape   = ["get platform", 0, false, "function platform() {\\n    [native code]\\n}"]
```

### 一、这一轮踩的两个坑（都值得记）

1. **`{ get x() { … } }.x` 会立刻调用 getter** —— `this` 是那个对象字面量，守卫当场抛出，
   整段 per-name 循环被吞掉，什么都没装上。原版用的是
   `Object.getOwnPropertyDescriptor({ get m(){…} }, 'm').get` —— **取描述符，不取值**。
2. **从原型上读值是错的**：`Navigator.prototype.platform` 在真浏览器里抛出
   `Illegal invocation`（原生访问器绑定接口）。值要从**实例**读 —— `G.navigator[name]`。

3. 顺带：`asNative` 存进 FAKES 的源码也要**抹掉访问器角色**，
   否则我们自己的访问器答 `function get userAgent() {…}`，而设备答 `function userAgent() {…}`。

### 二、另一半：补丁用**路径**记录，供子 realm 重放

```js
const record = (target, name) => {
  const path = pathOf(target);          // ['Navigator','prototype'] / ['Intl','DateTimeFormat','prototype']
  if (path) PATCHES.push({ path, key: name, from: target });
};
```

`KNOWN` 二十三个构造器 + `Intl` 九个名字，构成「一个对象在另一个 realm 里叫什么」的答案。

> **同源 iframe 有自己的构造函数。** 不按路径重放，`iframe.contentWindow.navigator` 会把真实 Blink 值原样交回来。

### 三、这一轮的一句话

> 「我装了这个值」和「我装了一个原生访问器」之间，差的是**一次 throw**。
>
> **检测器不需要参考设备，只需要一个空对象当接收者。**
'''

if "## 外来接收者要**抛异常**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("brand check documented")
else:
    print("already present")
