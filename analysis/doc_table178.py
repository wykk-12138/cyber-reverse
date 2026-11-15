import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 三十四个打点，不是「导航器加几个补丁」（第 178 轮）

把池子里所有 `method(target, name, build)` 的调用点扫出来 —— **34 个不同位置**：

| 区域 | 数量 | 内容 |
|---|---|---|
| canvas | 6 | `measureText` `fillRect` `arc` `getImageData` `getContext` `toDataURL` |
| webgl | 4 | `getParameter` `getSupportedExtensions` `getContextAttributes` `getShaderPrecisionFormat` |
| audio | 2 | `AudioBuffer.getChannelData` `HTMLAudioElement.canPlayType` |
| date-intl | 10 | 5 个 `Date.prototype`、`DateProxy` 三件、`Date.parse`、`Intl.DateTimeFormat` |
| core | 3 | **`Function.prototype.bind`**、**`JSON.stringify`**、**`Reflect.ownKeys`** |
| other | 9 | `matchMedia` `Performance.now` `createEvent` `StorageManager.estimate` `getComputedStyle` `getVoices` 等 |

### 一、为什么这张表本身是结论

看到 `Function.prototype.bind`、`JSON.stringify`、`Reflect.ownKeys` 都在里面，就知道
**「注入的边界不在 navigator」**：它改写的是**读的方式**，不只是**被读的值**。

> `JSON.stringify` 在名单里，意味着「你把 navigator 序列化给我看」这条路已经被算进去了。

### 二、本工作区已实现 13 个，缺 21 个

```
canvas 6 / webgl 1 / date-intl 3 / core 0 / other 2   →  13
```

`TheGapIsANumber` 把差额算成数字并且逐条列名 —— **缺口是一个清单，不是一种感觉**。

### 三、一个自查出来的错

我第一版写「webgl 只有 2 个」（`getParameter` + `getSupportedExtensions`），实测 4 个；
五个区域相加只有 25，剩下的 **9** 个没有归属。断言「和必须等于 34」立刻把它抓出来，
于是 `ByArea()` 多了一个显式的 `other` 桶，把那九个名字打出来。

> **给分类加一条「必须加总」的断言，是为了让「我漏了一类」变成红色。**

### 四、这一轮的一句话

> 三十四个打点里，只有三个在 `navigator` 上。我过去两周一直在 `navigator` 里打转。
>
> **清单能纠正的不是记性，是视野。**
'''

if "## 三十四个打点" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("table documented")
else:
    print("already present")
