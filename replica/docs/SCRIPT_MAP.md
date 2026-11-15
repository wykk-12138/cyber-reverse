# 注入脚本的字节地图（R187）

`target\Cybersole.exe`（123.3 MB）里，机器人注入的整段 JS 是**一段连续文本**，而且它是**窄字面量（ASCII）**，
不是 UTF-16 —— `analysis\pe_strings.py` 两种都收（先收 UTF-16 段、再收 ASCII 段），所以表里的地址列是
**文件偏移**，同一段文本内偏移顺序即语句顺序。

**偏移 → 虚拟地址**（`.rdata`，imagebase `0x140000000`）：

```
0x03d05776 → 0x143D05776      0x03d1efd4 → 0x143D1EFD4
0x03d208ca → 0x143D208CA      0x03d272d4 → 0x143D272D4
0x03d99162 → 0x143D99162
```

已验证：把 `0x143D1EFD4` 交给 IDA 的 `py_eval` 读 64 字节，回来的正是
`    ['getOwnPropertyNames', 'keys'].forEach((name) => {` —— 文件偏移与库内地址对得上，同一份文本。

> 踩过的坑：先用 `utf-16-le` 解这段会得到乱码（`'\u6174\u6772…'`），因为它是 ASCII；
> 一度以为偏移算错了。**先确认字面量的编码，再谈顺序。**


## 一、关键偏移

| 偏移 | 语句 | 说明 |
|---|---|---|
| `0x03d03cfe` | `var ce = this,` | 打包器尾部（无关） |
| `0x03d053cf` | `const G = typeof globalThis !== 'undefined' ? globalThis : self;` | 注入 IIFE 开始 |
| `0x03d05639` | `const nativeToString = Function.prototype.toString;` | **引用捕获 #1** |
| `0x03d05776` | `const nativeOwnNames = Object.getOwnPropertyNames;` | **引用捕获 #2**（本轮的根） |
| `0x03d057fc` | `const asNative = (fn, name) => cloak(...)` | 伪装入口 |
| `0x03d06d69` | `const PATCHES = [];` | 补丁日志 |
| `0x03d06fb8` | `let NAV_PRUNE = null;` | 三个 prune 先占位 |
| `0x03d08a2f` | `const reseat = (proto, order) => {` | 重排 |
| `0x03d08d45` | `const method = (target, name, build) => {` | 带记录的补丁器 |
| `0x03d0a917` | （注释）"actually observed being asked about are reordered; everything else delegates untouched" | 收窄的理由 |
| `0x03d1cf…` | `WINDOW_ALL` / `WINDOW_ENUM` / `CSS_DECL` / `CSS_VOCAB` 常量表 | 1062 / 228 / 881 … |
| `0x03d1de57` | `const MAIN_FRAME_ONLY = new Set(['_injected_scroll_helper', '_injected_navigation']);` | 两个仅主框架的名字 |
| `0x03d1deb2` | `const topList = (all, names, enumerableOnly) => {` | 排序函数 |
| `0x03d1e1bf` | `const reorder = (target, names, enumerableOnly) => {` | 分派：窗口 / CSS / ORDER 表 |
| **`0x03d1efd4`** | **`['getOwnPropertyNames', 'keys'].forEach(...)` + `method(Reflect,'ownKeys',...)`** | **键序层安装点** |
| `0x03d1f412` | 超越函数修正（`Math.cos(13*Math.E)`、`Math.tan(6*Math.LN2)`） | libm 指纹 |
| `0x03d2070c` | `Object.keys(NAV).forEach(...)` | navigator 安装 |
| **`0x03d208ca`** | **`NAV_PRUNE = (realm) => {`** | 用 `nativeOwnNames` 枚举 |
| `0x03d20953` | `nativeOwnNames(proto).forEach(...)` | 就是上面那条引用 |
| `0x03d222d6` | `NAV_PRUNE(G);` | 立即执行 |
| **`0x03d272d4`** | **`GLOBAL_PRUNE = (realm) => {`** | 白名单删除 |
| `0x03d27321` | `nativeOwnNames(realm).forEach(...)` | 同上 |
| **`0x03d27858`** | **`DOCUMENT_PRUNE = (realm) => {`** | 8 个 Blink-only 成员 |
| `0x03d98a97` | `if (NAV_PRUNE) NAV_PRUNE(child); if (GLOBAL_PRUNE) ...` | 子 realm 三连 |
| **`0x03d99162`** | **`if (isWindow) { try { WINDOW_BASELINE = new Set(nativeOwnNames(G)); } catch (e) { } }`** | **最后一句** |

## 二、两个结论

**1. 键序层装在 prune 之上，而且这是安全的。**
`0x03d1efd4` < `0x03d208ca` < `0x03d272d4` < `0x03d27858`。之所以能这样，是因为三个 prune 枚举时用的是
`nativeOwnNames`——在任何替换发生之前就抓住的引用。**顺序不重要，是因为引用被握住了**，不是因为顺序挑得巧。
R186 我把包装器挪到 prune 之后（怕它过滤掉 `MAIN_FRAME_ONLY` 里的两个名字），那是猜的；R187 按字节改回来了，
并且补上了 `NativeRefs` 这一步。

**2. `WINDOW_BASELINE` 是最后一句，且用同一个引用。**
`0x03d99162` 在所有安装、所有 prune、子 realm 钩子之后。它取的是"脚本装完之后真正的自有一览"，
所以脚本自己加的槽位不会被当成页面定义的。

## 三、键序层的确切形状（`0x03d1efd4`）

```js
['getOwnPropertyNames', 'keys'].forEach((name) => {
  method(Object, name, function (original, args) {
    return reorder(args[0], original.apply(this, args), name === 'keys');
  });
});
method(Reflect, 'ownKeys', function (original, args) {
  const keys = original.apply(this, args);
  const strings = [], rest = [];
  keys.forEach((k) => { (typeof k === 'string' ? strings : rest).push(k); });
  if (!rest.length) return reorder(args[0], keys, false);
  return reorder(args[0], strings, false).concat(rest);
});
```

- **三个入口**，不是两个。
- `reorder` 只对 `isWindow && target === G` 生效 —— "only the real global object, not something that merely looks
  like it"。R186 的 `target.window === target && target.document` 太宽。
- 走 `method()` 安装 ⇒ **补丁被记录**，子 frame 会收到同一份描述符。
- `Reflect.ownKeys` 先按 `typeof === 'string'` 拆开再拼回去，理由是"反正符号本来就排最后"，
  而旧写法"有符号就整个放弃"会让 `getOwnPropertyNames` 和 `ownKeys` 对同一对象给出不同答案。

## 四、仍然没接线的部分（`reorder` 内部）

R188 之后只剩一块：CSS 那一支的**完整版**（`CSSStyleProperties` 合成 + Proxy）。施工图见
`docs\CSS_PROPERTIES_PLAN.md`，数据与代码形状都已从下面的偏移读出来。

| 偏移 | 语句 | 状态 |
|---|---|---|
| `0x03d0a9c6` | `const ORDER = [` 11 条规则（17.7 KB） | **已接线**（`KeyOrderRules`） |
| `0x03d15574` | `const CSS_DECL = [...]` 11 个名字 | **已接线**（原型分支） |
| `0x03d1eb7b` | 实例分支（只报数字索引，**不受 `!enumerableOnly` 约束**） | **已接线** |
| `0x03d156xx` | `CSS_PROPS` / `CSS_VOCAB` 1468 个名字（两份完全相同） | **已接线**（`CssProperties`，R189） |
| `0x03d98/9…` | `CSSStyleProperties` 合成 + `CSS_PROTO` + `toStringTag` + 两个 WebKit 名字补实 | **已接线**（`CssStyleProperties`，R189） |
| `0x03d98…` | `Proxy`（ownKeys/has/getOwnPropertyDescriptor/get/getPrototypeOf）+ `method(G,'getComputedStyle')` | **已接线**（R189） |

> `KeyOrderTable.BodyJs()`（R180 那份 150 行）**已删除** —— 它是第二份没人调用的实现，正是本仓库反复出现的
> 「调用存在、没人调用它」缺陷。表与常量留在 `KeyOrderTable`，分发在 `WindowOrderWrap`。

