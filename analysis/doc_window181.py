import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 窗口上那十一个 `_injected_*`（第 181 轮）

把原版那张顶层名字表数出来：**1290** 个名字。前二十个里就有这些：

```
_injected_programmatic_form_submission_handler   _injected_clipboard
_injected_setup_frame                            _injected_passkey_controller
_injected_autofill_form_features                 _injected_scroll_helper
_injected_navigation                             _injected_gcrweb
_injected_choose_file                            _injected_print
gcrweb                                           __gCrWeb
```

这是 **Chrome for iOS 自己的注入钩子**。我们的窗口一个都没有 —— 这是一个**设备级指纹**，
再多 navigator 上的修补也补不平：页面只要 `Object.keys(window)` 就能看出来。

### 一、为什么不能写成常量

```
// The TOP-LEVEL list cannot be a constant, because api.js hands the host page's globals to hsw:
//   function sr(){ return Object.keys(window).sort().join(",") }      // called from initChallenge
// goes into the create-challenge message as `wdata`, the frame stores it as window.__wdata, and
// the wasm reads it back (4 Reflect.get per solve; the proof grows with it).
```

所以答案是**实时**键表，且顺序要刻意安排。`WINDOW_BASELINE` 就是那个机制：

```
// Every own name the engine reported for this window once this script had finished installing --
// document-start, before any page script. Assigned on the LAST line of the file. Whatever the
// engine reports later that is not in here, the page put there.
```

### 二、帧与顶层不是同一张表

```js
const FRAMED = (() => { try { return isWindow && G.top !== G; } catch (e) { return true; } })();
const MAIN_FRAME_ONLY = new Set(['_injected_scroll_helper', '_injected_navigation']);
```

「a frame advertised two names its real counterpart lacks」—— 所以子帧要**少两个**名字，
而不是多两个。

### 三、`CSS_DECL` 只有十一个名字

```
["constructor","cssText","cssRules","length","parentRule","item",
 "getPropertyValue","getPropertyPriority","setProperty","removeProperty","getPropertyCSSValue"]
```

对比上一轮读到的「~1500 属性访问器在 `CSSStyleProperties` 上」—— **原型短、实例只有数字索引**，
两句合起来才是 WebKit 的形状。Blink 没有 `CSSStyleProperties`，它把驼峰属性挂实例、另外暴露 `cssFloat`。

### 四、这一轮的一句话

> 我一直在 `navigator` 上找差距，而最大的差距在 `Object.keys(window)` 里 —— **十一个别人有、我们没有的名字**。
>
> **指纹不只在被读的对象上，也在「有哪些对象」这件事上。**
'''

if "## 窗口上那十一个" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("window baseline documented")
else:
    print("already present")
