import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 被漏掉的那半几何：`VisualViewport`（第 151 轮）

原版注释早就说过：

> innerWidth/innerHeight and visualViewport were the only geometry left unpatched, so they reported
> the real host window while outerWidth/outerHeight reported the device.

**replica 在修完前半句之后，正好又犯了后半句。** 这轮补上。

### 一、逐字取回的对象

```
const SCREEN = {"width":402,"height":874,"availWidth":402,"availHeight":874,
                "availLeft":0,"availTop":0,"colorDepth":24,"pixelDepth":24};
const SCREEN_ORDER = ["height","width","colorDepth","pixelDepth","availLeft","availTop",
                      "availHeight","availWidth","orientation"];
const VV = {offsetLeft:0, offsetTop:0, pageLeft:0, pageTop:0, width:VW, height:VH, scale:1};
```

### 二、两个新结论

**① `VisualViewport` 是七个字段**，值 `402 / 684 / scale 1 / offsets 0`，只装在顶层（它是窗口的视口，不是 frame 的）。
已进 `MobileSurface.VisualViewportFields` 与 `BodyJs()`；真浏览器测到 `[402,684,1,0,0]`。

**② `orientation` 在 `SCREEN_ORDER` 里，却不在 `SCREEN` 值对象里** —— 原版**不补**它的值。
实测这台机器报 `landscape-primary`、angle 0，而 profile 声称竖屏手机 —— **这是一处已知的不自洽**。

我不替它编一个值（那就成了「发明行为」），但也不让它沉默：运行时测试把 `orientation` 打印出来，
并断言它确实是「两个原生值之一」，同时在文档里记下这条矛盾。

> **留白要有名字。** 什么都不写的留白，和写着「这里已知不自洽」的留白，不是一回事。

### 三、四 + 一 条测试

`VisualViewportTests` 四条（七字段与顺序、orientation 只在形状里、视口只在顶层、
值与 `scale: 1` 且块内无 `throw`）；运行时测试新增视口与 orientation 两段测量。

### 四、这一轮的一句话

> 上一轮我以为「几何已经全对了」。原版那句注释里，我修的是 `innerWidth/innerHeight`，
> 而它同时点名了 `visualViewport` —— **同一句话里的两件事，我只做了一件，还以为句子读完了。**
'''
if "## 被漏掉的那半几何" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("viewport documented")
else:
    print("already present")
