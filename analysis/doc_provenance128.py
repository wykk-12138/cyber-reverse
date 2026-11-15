import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 溯源闸门：端点必须**逐字**出现在镜像里（第 128 轮）

上一条规则（「主机 + 路径必须来自同一条字面量」）这一轮变成了**机械检查**。

### 工具：`tools/endpoint-provenance.py` → 验证第 8 步

它做两件事：

1. 把 `src/Cybersole.Stores/Flows/*.cs` 里所有**端点常量**找出来；
2. 把 `Base + "/path/"` 这种**拼出来的**常量按嵌套类作用域**解引用成完整值**，
   然后逐字到 `analysis/pe_strings.txt` 里找。

```
endpoint constants: 159   verbatim in pool: 159   invented: 0   unresolved: 0
```

**159 / 159 逐字命中，0 编造。** 这条现在是 `verify-steps.ps1` 的第 8 步。

### 写这个工具时踩的两个坑（都是「我的检查器坏了」，不是端点坏了）

**坑一：把字典当列表迭代。** `for name, value in plain:` 对着 dict 跑，直接
`ValueError: too many values to unpack`。

**坑二（重要）：嵌套类共享常量名，扁平解析会串味。**

`RetailApiFamilies.cs` 里 `ScheelsFrontastic` 和 `JohnLewisBff` **各自**声明了一个 `Base`。
我把整个文件当一个作用域收集常量，字典 last-wins，于是 John Lewis 的路径被拼到了
Scheels 的主机上，报出 13 条假的「编造」。

修法：**先把嵌套类区间从外层文本里挖空**，再收集本层常量，解析时按「内层 → 外层」查。

```
修前：invented: 19      修后：invented: 0
```

> **检查器自己错了，比被检查的代码错了更危险** —— 它会让你去「修」本来正确的代码。
> 所以这一轮我改了两次工具，一次也没有动端点。

### 与 GUI 的关系

这一轮没用 GUI。它是纯字节侧的闸门 —— **GUI 无法回答「这个端点是不是我拼出来的」**，
因为界面上两个端点看起来都只是「一个设置项」。
'''

if "## 溯源闸门" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("provenance gate documented")
else:
    print("already present")
