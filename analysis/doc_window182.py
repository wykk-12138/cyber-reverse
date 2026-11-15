import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 把十一个名字放到窗口上（第 182 轮）

上一轮只是**读**到了那十二个名字，这一轮**装上去**，并且验证两件页面能验证的事。

### 一、装在链尾，且必须装在链尾

```csharp
surfaceBody += WindowBaseline.BodyJs();   // 十一个全局名 + 基线
surfaceBody += MaskTargets.ApplyJs();     // 最后
```

理由写在 `SurfaceOrder` 第 10 步：**它们是全局名，而它报告的基线是「本脚本装完之后」的自有名字表**
—— 早装一步，基线就会漏掉后面装的东西。

### 二、实测

```
probe = [6,"object",false,12]
          ↑六个抽样名都在  ↑__windowBaseline 是对象  ↑framed=false（顶层）  ↑12 个注入名
Object.keys(window) 里有 __gCrWeb 和 _injected_clipboard  →  true:true
```

子帧：

```
child = [false,false,true,true]
          ↑_injected_scroll_helper 不在  ↑_injected_navigation 不在  ↑__gCrWeb 在  ↑gcrweb 在
```

**两个名字被去掉、其余保留** —— 正是「a frame advertised two names its real counterpart lacks」的反面。

### 三、为什么这比 navigator 上的修补更有分量

`navigator` 上的每个值都可能被一个「更聪明的」检测器怀疑；而 `Object.keys(window)` 的长度和内容
是**结构性**的：要么有这个名字，要么没有。

> 我们之前所有的修补，都发生在**页面已经知道存在的对象内部**；这一轮第一次改变**对象清单本身**。

### 四、这一轮的一句话

> 抄一个值，只能骗过读这个值的检测；抄一个**名字**，骗过的是「这台设备上有什么」的检测。
>
> **后者的成本高一个数量级，收益也是。**
'''

if "## 把十一个名字放到窗口上" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("documented")
else:
    print("already present")
