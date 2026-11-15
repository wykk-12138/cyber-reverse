import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 页面的全局名不该被删，该被**放到后面**（第 185 轮）

上一轮留下了这个问题：`GLOBAL_PRUNE` 删「设备没有的名字」，那页面自己加的 `window.foo` 怎么办？

答案在原版的 `topList` 里 —— **它不删，它排**：

```js
const topList = (all, names, enumerableOnly) => {
  const base = FRAMED ? all.filter((n) => !MAIN_FRAME_ONLY.has(n)) : all;
  if (!WINDOW_BASELINE) return base.slice();
  const known = new Set(base);
  const indices = [], defined = [];
  names.forEach((name) => {
    if (WINDOW_BASELINE.has(name) || known.has(name)) return;      // 已知 → 不动
    (/^(0|[1-9][0-9]*)$/.test(name) ? indices : defined).push(name); // 页面加的 → 分类
  });
  const out = indices.concat(base, defined);                        // 索引在前，基表居中，具名在后
  …
};
```

### 一、基线必须是**最后一句**

```
// MUST stay the last statement. The snapshot has to include everything installed above, or the slots this script
// added itself would later be reported as something the page defined.
if (isWindow) { try { WINDOW_BASELINE = new Set(nativeOwnNames(G)); } catch (e) { } }
```

早一句，脚本自己装的东西就会被当成「页面的」，于是**被排到最后**——顺序立刻变形。

### 二、`webkit` 的补丁只在一处

```js
if (enumerableOnly && !FRAMED && names.indexOf('webkit') !== -1 && out.indexOf('webkit') === -1) {
  const at = out.indexOf('Raven');
  out.splice(at === -1 ? out.length : at, 0, 'webkit');
}
```

`webkit` 在自有名表里、**不在**枚举表里，所以枚举那一遍要显式插到 `Raven` 之前。

### 三、实测

```
shape  = ["function"…]         __topList 在、__windowBaseline.names 有 1000+ 项
order  = ["Raven",true,true]   页面具名全局落在最后，且排在 Raven 之前
splice = [876,-1,true]         webkit 被插到 876 位（本次 all 里没有 Raven，于是追加）
```

### 四、顺手抓到自己踩的坑

第一次跑 `__topList` 是 `undefined` —— 因为 `GLOBAL_PRUNE` 把它删了（它不在 KEEP 里）。
**这正是 prune 该有的行为**，也说明 KEEP 必须覆盖自研内部名：`__topList`/`__globalPrune`/`__documentPrune` 已补进 KEEP。

### 五、这一轮的一句话

> 上一轮我以为答案是「谁该被删」，这一轮发现答案是「谁该被排在后面」。
>
> **很多时候「删掉」是最粗的修法；排序才是原版的做法 —— 它保留了信息，只改变读到的次序。**
'''

if "## 页面的全局名不该被删" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("documented")
else:
    print("already present")
