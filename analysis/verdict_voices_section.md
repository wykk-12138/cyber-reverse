### `getVoices()` 返回空数组，和「无 src 的 iframe 永不触发 load」

R136 改完 realm 重放，这一轮读了 `INJECTED_GLOBALS` 周边那段注释，找到两个真缺口。

### hCaptcha 的检测函数 `Oe`

注释里抄下了它：

```js
Oe = (o,n) => { const d = gOPD(o,n), fn = d && (d.value || d.get);
                return typeof fn === 'function' && fn.toString() === `function ${fn.name}() {\n    [native code]\n}`; }
```

**它扫窗口最后 25 个名字，KEEP（不上报）任何「值或 getter 是 native 样子函数」的。**

原版为了通过它，把 `webkit` 做成了：

```js
if (INJECTED_GLOBALS.has(name)) {
    Object.defineProperty(G, name, {
        value: Object.create(Ctor.prototype), writable: true,
        enumerable: ENUMERABLE.has(name) || (name === 'webkit' && !FRAMED), configurable: true,
    });
    return;
}
value(G, name, Object.create(Ctor.prototype), ENUMERABLE.has(name));   // 默认：访问器
```

**数据属性而不是访问器**——因为：

> An accessor-backed `webkit` hands Oe a native-looking getter, **passes the sweep, and drops out of the suspicious-globals list**. The iPhone's `webkit` is an **OBJECT, fails Oe, and is reported**. Measured: device `["__gCrWeb","hsw","__wdata","webkit"]`, ours had no `webkit` at all.

**「通过检测」和「和真机一致」是两件相反的事。** 做成访问器反而让 `webkit` 从可疑列表里消失，
而真机上它**是在列表里的**。**所以伪造得越「干净」越容易被抓。**

### 但这一套 replica 不需要

| 原版 | replica |
|---|---|
| 伪造 **iOS Chrome**（`CriOS/156`） | 伪造 **Windows 桌面 Chrome**（`Windows NT 10.0`） |
| 需要 `webkit`（Safari/WebKit 专有） | Chrome 没有 `webkit` |
| 需要 `_injected_scroll_helper` / `_injected_navigation`（Chrome-iOS 注入） | Windows 没有 |
| 需要伪造 `Object.keys(window)` 顺序 | 真实 Chrome，顺序天然正确 |

**`MAIN_FRAME_ONLY`、`GLOBAL_KINDS`、`TOP_ORDER` 那一整套，是为了让一个嵌入式 Chromium
在 iOS 上看起来像 iOS。replica 跑的是真的 Windows Chrome，那些属性本来就对。**

**这不是「replica 做得少」，是「它面对的问题更少」。**

### 缺口一：`getVoices()` 返回空数组

```
grep speechSynthesis|getVoices|SpeechSynthesis  →  0 命中
```

**无头 Chrome 的 `speechSynthesis.getVoices()` 返回 `[]`。**

原版：

```js
const VOICES = [{"voiceURI": "com.apple.voice.super-compact.nl-BE.Ellen", "name": "Ellen", ...}];
const voiceTarget = (has('SpeechSynthesis') && G.SpeechSynthesis.prototype
    && typeof G.SpeechSynthesis.prototype.getVoices === 'function')
    ? G.SpeechSynthesis.prototype
    : G.speechSynthesis;
method(voiceTarget, 'getVoices', function () { return VOICES.slice(); });
```

**`getVoices().length === 0` 是最便宜的检测之一**：任何平台上的真实浏览器都不会只有零个语音。
一行就能判定无头。

**修**：6 个 Windows Chrome 的语音（`Microsoft David` / `Zira` / `Mark` + `Google US English` /
`UK English Female` / `UK English Male`），装在原型上，实例上没有时退到实例。

### 缺口二：无 src 的 iframe 永不触发 load

R136 我用 `el.addEventListener('load', ...)` —— **原版的注释说这不够**：

> Injection does not save us either — **a frame created with `createElement`/`appendChild` never
> navigates, so there is no document-start for the host to hook.** Replay the recorded patches
> instead, **at the moment the page reaches for the child.**

**一个没有 `src` 的 iframe 是 `about:blank`，永远不导航，永远不发 `load`。**

而检测方最常用的恰恰就是这个：建一个空 frame，插进 DOM，读它的 `navigator`。

**修**：`createElement` 里**同步** replay 一次，`load` 作为导航型 frame 的补充。

```js
if (String(tag).toLowerCase() === 'iframe') {
    replay(el.contentWindow);                                    // 无 src 的情况
    el.addEventListener('load', () => replay(el.contentWindow));  // 会导航的情况
}
```

**两条路都要走**，因为这是两种 frame。

### 还有一个没做的：prune

原版有 `NAV_PRUNE` / `GLOBAL_PRUNE` / `DOCUMENT_PRUNE`，注释说：

> Deletions are not descriptors, so they have to be replayed separately or the child still
> advertises the Blink-only navigator APIs — and, until `GLOBAL_PRUNE` was replayed here too, the
> Blink-only GLOBALS: **an audit found `chrome` present in the iframe while absent at the top,
> which is a worse answer than either alone.**

**顶层删掉的东西，子 realm 也要删。** 否则子 frame 上多出来的东西本身就是信号——
**「两边不一致」比「两边都错」更容易被抓。**

**replica 现在没有删除型补丁，所以暂时不需要 prune。** 但这条要记下来：
**将来加第一个删除型补丁时，必须同时加 prune 重放。**

### 验证

```
dotnet test      639 通过 / 0 失败 / 2 跳过   (+2)
live contracts   PASS
store modules    PASS 61 registered
try blocks       13（8 补丁 + getVoices + 2 次 iframe 钩子 + 兜底）
voice entries    6
```

---
