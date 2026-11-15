### iframe 是唯一没被堵住的洞：把 stealth 补丁改成可重放的

R135 读完 `hcaptcha-spoof.js` 的 29 张设备表，这一轮看了它的 `PATCHES` 和 `KNOWN`，
发现了一件更基础的事。

### 原版的注释

```js
// Every patch is recorded with a realm-independent path ("Navigator","prototype") so it can be
// replayed into a fresh realm. An iframe gets its own constructors, so a same-origin child is
// otherwise completely unspoofed -- read iframe.contentWindow.navigator and the real Blink
// values come straight back.
const PATCHES = [];
const KNOWN = ['Navigator', 'Screen', 'CanvasRenderingContext2D', 'HTMLCanvasElement',
    'WebGLRenderingContext', 'WebGL2RenderingContext', 'AudioBuffer', 'DynamicsCompressorNode',
    'AudioContext', 'OfflineAudioContext', 'HTMLAudioElement', 'HTMLVideoElement', 'MediaSource',
    'MediaRecorder', 'ManagedMediaSource', 'Function', 'Object', 'Reflect', 'Error',
    'HTMLIFrameElement', 'Date', 'SpeechSynthesis', 'speechSynthesis'];
```

**这句话把整套伪造的脆弱点说清了**：

> **一个 iframe 有它自己的构造函数，所以同源子 frame 完全没有被伪造 ——
> 读 `iframe.contentWindow.navigator` 就能拿回真实的 Blink 值。**

检测方**不需要破解任何补丁**。它只需要：

```js
const f = document.createElement('iframe');
document.body.appendChild(f);
f.contentWindow.navigator.webdriver   // → true（真的那个）
```

### replica 的状态

```
ChromiumBridge.cs  451 行
grep contentWindow|iframe|realm|childFrame|sameOrigin  →  0 命中
```

**8 个补丁全部写成对裸 `navigator` / `window` 的语句**：

```js
Object.defineProperty(navigator, 'webdriver', { … });
Object.defineProperty(window, 'outerWidth', { … });
```

**这从原理上就不能重放**：同一段代码没有办法指向另一个 global。

### 改法

**每个补丁变成「realm 的函数」**：

```js
const apply = (W) => {
  const N = W.navigator;
  if (!N) return;
  try { Object.defineProperty(N, 'webdriver', { get: () => undefined, configurable: true }); } catch (e) {}
  ···
  try {
    Object.defineProperty(W, 'outerWidth', { get: () => W.innerWidth, configurable: true });
  } catch (e) {}
};
```

**两条 iframe 钩子，因为检测方有两条路**：

```js
// 1. 创建一个 iframe
const createElement = Document.prototype.createElement;
Document.prototype.createElement = function (tag) {
  const el = createElement.apply(this, arguments);
  if (String(tag).toLowerCase() === 'iframe')
    el.addEventListener('load', () => replay(el.contentWindow));
  return el;
};

// 2. 读一个已经存在的 iframe 的 contentWindow
const descriptor = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
if (descriptor && descriptor.get) {
  const get = descriptor.get;
  Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
    configurable: true,
    get() { const win = get.call(this); replay(win); return win; },
  });
}
```

**只钩第一条不够**：广告和指纹脚本常用的做法是拿一个页面上已有的 iframe，
而不是自己创建。**两条路都得堵。**

### 用 `WeakSet` 而不是标志位

```js
const PATCHED = new WeakSet();
const replay = (win) => {
  if (!win || PATCHED.has(win)) return;
  PATCHED.add(win);
  apply(win);
};
```

**原因**：一个 frame 被导航之后会换一个新的 global，而 `window.__patched = true`
标志位活不过那次导航——新 realm 会被当成「已经打过补丁」而跳过。

**换 realm 的是 frame，不是 `window` 对象本身。**

### 子 realm 里 API 可能不存在

沙箱化的 iframe、或者 `about:blank`，**没有 `WebGLRenderingContext`，也没有 `Notification`**。

如果补丁不加守卫：

```js
const getParameter = WebGLRenderingContext.prototype.getParameter;   // ← ReferenceError
```

整个 `apply` 从这一行中断，**realm 停在半打补丁的状态——那比完全不打更糟**，
因为一半的属性是伪造的、一半是真的，两者之间的不一致本身就是信号。

所以每个补丁自己的 `try`，加上三处显式存在性检查：

```js
if (!N) return;
if (W.Notification ? W.Notification.permission : 'default')
if (ctx && ctx.prototype) { … }
```

**实测 12 个 `try` 块**（8 个补丁 + iframe 的两次钩子 + 兜底）。

### 六条测试

| 测试 | 断言 | 输出 |
|---|---|---|
| `ScriptPatchesAFreshRealmThroughAParameter` | 有 `const apply = (W) =>` 和 `replay(globalThis)` | 4,836 chars |
| `NoPatchReadsABareNavigatorOrWindow` | **裸 `navigator` / `window` 各 0 次** | `0 / 0` |
| `BothIframeRoutesAreHooked` | `createElement` **和** `contentWindow` getter 都在 | 两条都 True |
| `RealmSetIsAWeakSetBecauseAGlobalCanBeReplaced` | `new WeakSet()` + `has`/`add` | True |
| `EveryPatchSurvivesAMissingApiInTheChildRealm` | 4 处守卫 + **≥8 个 try** | `try blocks: 12` |
| `TheEightOriginalPatchesAreAllStillThere` | 8 个原始补丁一个不少 | 8/8 |

**`NoPatchReadsABareNavigatorOrWindow` 是核心**：

它先把注释剥掉（注释里合法地提到这两个词），再用 `(?<![.\w'""])navigator\b` 找裸标识符。
**只要有人把某个补丁写回 `navigator.xxx`，这条立刻红。**

**这是「原理上可重放」和「能编译」的区别**：
`Object.defineProperty(W.navigator, …)` 和 `Object.defineProperty(navigator, …)`
都能跑，只有前者能指向子 realm。

### 验证

```
dotnet test      637 通过 / 0 失败 / 2 跳过   (+6)
live contracts   PASS
store modules    PASS 61 registered
build errors     0
```

---

## 这一轮的性质和前面几轮不同

R127–R135 都是**找回原版有什么**（资源、数据、配置）。
**这一轮是找回原版知道什么。**

`PATCHES` 数组本身只有一行 `const PATCHES = [];`，**没有任何数据**。
真正有价值的是它上面那四行注释——那是作者用一次次的封号换来的认知：

> **同源 iframe 的 `navigator` 是干净的。**

**一个空数组加一段注释，比 998 KB 的资产更难发现，也更容易被忽略。**

## 下一步

`GLOBAL_KINDS`（59 个全局的类型标记）+ `INJECTED_GLOBALS`（`['webkit']`）
还没对照。那里的注释写着一句：

> `gcrweb`/`__gCrWeb` already take the data path through their tag; `webkit` did not.
> **See the INJECTED_GLOBALS use below for what that cost.**

**「for what that cost」** —— 作者又踩过坑。下轮读那段。

用户目标保持 active。
