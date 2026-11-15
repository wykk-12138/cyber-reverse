import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 挖到原版的隐身脚本本体：**WebAssembly 指纹**（第 146 轮）

本来在查 `SolveWafAsync` 挂在哪。查着查着撞到一段**带注释的注入脚本源码**，就停在它上面。

### 原文（镜像里的字符串，逐字）

```
// The challenge frame fingerprints WebAssembly directly. Its payload carries
//   ws[0] = [WebAssembly, Module.prototype, Instance.prototype, Memory.prototype, Table.prototype]
//              .map((o) => Object.getOwnPropertyNames(o).length)
// which Blink answers [19,1,2,5,5] and both iPhones that passed answer [16,1,2,6,6]. The gap is
// two features pointing in opposite directions: Chrome ships JSPI (Suspending, promising,
// SuspendError) which Safari does not, and Safari ships WebAssembly type reflection
// (Memory.prototype.type, Table.prototype.type) which Chrome does not. Dropping three and adding
// two lands on the device's numbers exactly. Only the counts are transmitted, but a type() that
// threw when called would be a worse answer than one returning the shape the proposal describes.
```

### 三件值得学的事

1. **数字是测出来的**：Blink `[19,1,2,5,5]`，通过的 iPhone `[16,1,2,6,6]`；
2. **方向相反才是要点**：Chrome 有 JSPI（三个名字），Safari 有 type reflection（两个方法）——
   所以修法不是「藏掉 WebAssembly」，而是**「让计数符合它声称的那台设备」**；
3. **stub 要回答，不能抛**：`a type() that threw … would be a worse answer` ——
   **一个会抛的方法本身就是信号**。

### replica 之前的样子

注入脚本补了 navigator / screen / WebGL，**从没碰 WebAssembly**。
于是挑战帧问这一个问题时，看到的是「声称某台设备、却答 Blink 的数字」。

### 已落成 `WebAssemblySurface`

- `BlinkCounts` / `SafariCounts` / `JspiNames` / `TypeReflectionTargets` 全部来自上面那段原文；
- `ToJavaScript()` 按原文做法：删三个、加两个非枚举方法、`name in target` 就不重复加；
- `StubRule` 把「不许抛」写成常量，测试断言脚本里**没有 `throw`**。

### 顺手记一个自己的错

`CountsDifferByTheDelta` 我第一版写成 `blink - safari == 3 - 2` ——**方向反了**。
正确的关系是：第一个数 19→16 对应「删掉三个」，而 5→6 对应「加上两个」落在另外两个原型上。
测试先红了一次才发现。

### 这一轮的一句话

> 我在查一个方法挂在哪儿，结果捡到了**原版写给人看的注释**。
>
> **带解释的代码是最好的证据** —— 它不只告诉你做什么，还告诉你作者当时在权衡什么。
'''

if "## 挖到原版的隐身脚本本体" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("wasm surface documented")
else:
    print("already present")
