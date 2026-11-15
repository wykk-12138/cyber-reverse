> **状态：已交付（R189）。** 施工图保留作参考；验收数字见本文第四节，实际测量全中，
> 见 `VERDICT.md` 第 189 轮。
# R189 施工图：CSSStyleProperties（原版 0x03d9… 那一段）

数据与代码形状都已从目标的注入脚本里读出来了。下面是照抄清单，写完即可用浏览器对账。

## 一、要生成的数据

| 数据 | 来源偏移 | 规模 |
|---|---|---|
| `CSS_PROPS`（= `CSS_VOCAB`，两份完全相同） | `0x03d156xx` / `0x03d9…`（第 159605 行） | **1468** 个名字，30.5 KB |
| 其中首字母大写（走 `-x` 前缀规则） | — | 190 |
| `webkit*` | — | 178 |
| `epub*` | — | 10 |

生成 `CssProperties.Generated.cs`（raw string，4 引号定界，勿手改）。

## 二、要写的代码（顺序即语义）

```js
// 1. 只在「有 CSSStyleDeclaration 且没有 CSSStyleProperties」时合成（Chrome 没有这个接口）
const dashed = (name) => name
    .replace(/^[A-Z]/, (c) => '-' + c.toLowerCase())
    .replace(/[A-Z]/g, (c) => '-' + c.toLowerCase());

const CSSStyleProperties = function CSSStyleProperties() {};
asNative(CSSStyleProperties, 'CSSStyleProperties');

const proto = Object.create(CSSStyleDeclaration.prototype);
// 2. constructor 先定义 —— getOwnPropertyNames 的顺序就是设备的顺序，不需要额外的 reorder 规则
Object.defineProperty(proto, 'constructor', { value: CSSStyleProperties, writable: true,
                                              enumerable: false, configurable: true });
// 3. 每个名字一对 get/set，内部走 getPropertyValue / setProperty
CSS_PROPS.forEach((name) => {
  if (name === 'constructor') return;
  const css = dashed(name);
  const getter = noProtoGetter(function () { return this.getPropertyValue(css); });
  asGetter(getter, name);
  const setter = noProtoSetter(function (v) { this.setProperty(css, v); });
  asGetter(setter, name);                       // 原版这里就是 asGetter，不是 asNative
  Object.defineProperty(proto, name, { get: getter, set: setter, enumerable: true, configurable: true });
});
CSSStyleProperties.prototype = proto;
CSS_PROTO = proto;                              // ← reorder 的第 3 条分支靠它排除「接口原型」
Object.defineProperty(proto, Symbol.toStringTag,
  { value: 'CSSStyleProperties', writable: false, enumerable: false, configurable: true });
Object.defineProperty(G, 'CSSStyleProperties', { value: CSSStyleProperties, ... });

// 4. CSS_DECL 里那两个 WebKit 独有的名字必须真的存在，否则「枚举得到 / descriptor 是 undefined」
const gpcv = noProtoMethod(function (property) { return null; }, 'getPropertyCSSValue');
Object.defineProperty(gpcv, 'length', { value: 1, configurable: true });
asNative(gpcv, 'getPropertyCSSValue');
Object.defineProperty(CSSStyleDeclaration.prototype, 'getPropertyCSSValue',
  { value: gpcv, writable: true, enumerable: true, configurable: true });
const cssRulesGetter = asGetter(noProtoGetter(function () { return null; }, 'cssRules'), 'cssRules');
Object.defineProperty(CSSStyleDeclaration.prototype, 'cssRules',
  { get: cssRulesGetter, enumerable: true, configurable: true });
```

## 三、Proxy（枚举之外的三条通道）

`delete` 对 Blink 的 camelCase 属性**无效**（IDL named-property interceptor，删了下次读又回来），
所以只能 Proxy。实测依据（原版注释）：747 个命名自有属性、0 个不可配置、0 个不可枚举 —— 因此 Proxy 不变量合法。

```js
const keep = (name) => typeof name !== 'string' || /^[0-9]+$/.test(name) || CSS_VOCAB.has(name);
const hidden = (t, p) => !keep(p) && Object.prototype.hasOwnProperty.call(t, p);
const indexKey = (p) => typeof p === 'string' && /^[0-9]+$/.test(p);
const BOUND = new WeakMap();

const wrap = (decl) => { if (!decl) return decl; return new Proxy(decl, {
  getPrototypeOf() { return proto; },
  ownKeys(t) { return nativeOwnNames(t).filter(indexKey).concat(Object.getOwnPropertySymbols(t)); },
  has(t, p) { return hidden(t, p) ? false : Reflect.has(t, p); },
  getOwnPropertyDescriptor(t, p) {
    if (hidden(t, p)) return undefined;
    if (typeof p === 'string' && !indexKey(p) && Object.prototype.hasOwnProperty.call(t, p)) return undefined;
    return Reflect.getOwnPropertyDescriptor(t, p);
  },
  get(t, p) {
    if (p === 'constructor') return CSSStyleProperties;
    if (p === Symbol.toStringTag) return 'CSSStyleProperties';
    const v = Reflect.get(t, p, t);
    if (typeof v !== 'function') return v;
    // Object.prototype 的内建**不能** bind：它们是泛型的，bind 会绕过代理，
    // 于是 decl.hasOwnProperty('appRegion') 与 Object.prototype.hasOwnProperty.call(decl,'appRegion') 两个答案
    try { if (Object.prototype[p] === v) return v; } catch (e) {}
    // 接口方法带 brand check，this 是 proxy 会抛 Illegal invocation → bind 到真对象，
    // 再把 name/length/toString 三样都还原（bound 函数自己会改名成 "bound getPropertyValue"）
    let bound = BOUND.get(v);
    if (!bound) {
      bound = v.bind(t);
      try { Object.defineProperty(bound, 'name', { value: v.name, configurable: true }); } catch (e) {}
      try { Object.defineProperty(bound, 'length', { value: v.length, configurable: true }); } catch (e) {}
      asNative(bound, v.name);
      BOUND.set(v, bound);
    }
    return bound;
  },
}); };

method(G, 'getComputedStyle', function (original, args) { return wrap(original.apply(this, args)); });
```

## 四、验收数字（同一台 Chromium，开/不开对照）

| 探针 | 现在（R188 之后） | 目标态 |
|---|---|---|
| `getComputedStyle(el).constructor.name` | `CSSStyleDeclaration` | `CSSStyleProperties` |
| `Object.prototype.toString.call(cs)` | `[object CSSStyleDeclaration]` | `[object CSSStyleProperties]` |
| `Object.keys(cs).length` | 480（全是索引） | 480（不变，但由 Proxy + reorder 双通道一致） |
| `'appRegion' in cs` | **true**（Blink 有） | **false** |
| `cs.hasOwnProperty('appRegion')` | **true** | **false** |
| `Object.getPrototypeOf(cs) === CSSStyleProperties.prototype` | false | true |
| `cs instanceof CSSStyleDeclaration` | true | **仍须 true** |
| `cs.getPropertyValue('color')` | 正常工作 | **仍须正常工作**（brand check 走 bind） |
| `getOwnPropertyNames(CSSStyleProperties.prototype).length` | 不存在 | 1468（constructor 第一） |

## 五、风险

1. **brand check**：接口方法从 proxy 上取会抛 `Illegal invocation` —— 必须先 bind 再返回，且 `constructor` 不 bind。
2. **`cssFloat` → `css-float`**：原版 `dashed()` 会把 `cssFloat` 变成 `css-float`，而正确的 CSS 名是 `float`。
   这是原版自身的一处可疑点，照抄即可（对账时若 `getComputedStyle(el).cssFloat` 取到空串，就记下来）。
3. **mutation-check** 与测试不能并发跑（R188 踩过：假红）。
