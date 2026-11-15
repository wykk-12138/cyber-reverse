import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 同一段注入脚本的其余部分：**iPhone 面的六条规则**（第 147 轮）

上一轮只读了 WebAssembly 那一块。把 `0x03d29000–0x03d2c800` 整段拉出来，151 条 —— 全是带注释的脚本。
每一条注释都在说「上一版被什么抓到了」。这些理由比数字值钱。

### 一、六条规则

| 规则 | 被抓的方式 |
|---|---|
| **TouchEvent 工厂要不抛** | Blink 的 `createEvent('TouchEvent')` 抛 `NotSupportedError`；于是页面「声称 iOS 26，却报触摸创建失败」，而 `'ontouchstart' in window`、`maxTouchPoints`、`TouchEvent` 构造器**在同一份 payload 里**说的相反 |
| **`performance.memory` 要删** | Blink 独有、WebKit 从未有过；hsw 直接探 `"memory" in performance`；它在 `Performance.prototype` 上，**窗口删除和 navigator 剪枝都碰不到** |
| **Screen 只能九个键** | Blink 多 `isExtended` / `onchange`（Multi-Screen Window Placement）；hCaptcha 整个 `for (var k in screen)` 抄走，**键的数量和位置都读**；十键的 screen 配 iPhone UA 自相矛盾 |
| **outer 与 inner 必须一起改** | 只改 outer 会造出 `innerWidth > outerWidth` 与 `innerWidth > screen.width` —— **真实浏览器造不出来** |
| **frame 里别改** | 设备数字是**顶层窗口**的；frame 里真实盒子才是诚实答案；但从未显示的 frame 布局是 0×0，**0×0 比「错但合理」更糟**，所以只有真有盒子时才保留原生值 |
| **`clientWidth` 要钉住** | hCaptcha 每次滚动推 `[scrollX, scrollY, clientWidth / min(innerWidth, clientWidth), now]`；innerWidth 假、clientWidth 真 → 比例 1.2437，滚动条占 15px 后变 1.2065 —— **iOS 滚动条是浮层，从不吃布局宽度，所以「会变的比例」是伪造不了的** |

### 二、两个可以拿去别处用的句子

> **「只改 outer 不改 inner，比两个都不改更糟。」**

> **「真正泄露的不是数字，是数字在本不该变的时候变了。」**

### 三、已落成 `MobileSurface`

`ScreenWidth 402` / `ScreenHeight 874` / `ChromeHeight 190` / `ViewportHeight 684` / `DevicePixelRatio 3`、
九键 `ScreenOrder`、`BlinkOnlyScreenMembers`、`Removed`（每条带探针）、`PinnedBoxes`、
`IsImpossibleGeometry`、`ZoomRatio`、`ScrollbarTell`、`FrameRule`。

### 四、一个诚实的差异

注释里写 `1.2437`，而 `500/402 = 1.24378…` **四舍五入是 1.2438** —— 原版是**截断**不是四舍五入。
测试改成比三位小数并附说明：**这一轮要钉的是「比例会变」这个事实，不是作者的取整习惯。**

### 五、这一轮的一句话

> 这些注释不是文档，是**战报** —— 每一条都记着「上一次被谁看穿了」。
>
> **能被读到的失败，比能被抄的成功更有信息量。**
'''

if "## 同一段注入脚本的其余部分" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("mobile surface documented")
else:
    print("already present")
