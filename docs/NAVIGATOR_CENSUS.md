# Navigator 普查（从 `replica/src` 迁出，R1273）

原先在 `replica/src/Cybersole.Stores/Scripts/NavigatorCensus.cs`。它记录的是 **R166 的测量结果**：镜像那 50 个
navigator 名字在本引擎里各住在哪。这是考据，按 `AGENTS.md` §3 归 `docs/`。

## 一、测量结果：50 个名字，三种归宿

| 归宿 | 数量 | 含义 |
|---|---|---|
| `Navigator.prototype` 自有属性 | **27** | 引擎有这些名字 —— 缺的是**值**，不是存在性 |
| 继承自 `Object.prototype` | **10** | `toString` / `valueOf` / `hasOwnProperty` / `__defineGetter__` 一族，不用动 |
| **完全缺席** | **13** | 手机有、这引擎没有 |

第三行是 `NavPrune` 的镜像，也是两份清单必须同时存在的原因。

## 二、为什么两个方向都要管

- WebKit **从来没有**的（`userAgentData`、`connection`、`bluetooth`）——手机若声称有，**必须装**；
- 手机有而引擎**没有**的（`standalone`、`credentials`、`mediaDevices`、`wakeLock`、`locks`、`storage`、`share`）——
  **必须补**，否则画像恰好缺了移动页要问的东西。

## 三、这轮就装上的两个（普通值，不需要额外工作）

```
standalone   （布尔）
locks        （对象，页面会调它的方法）
```

## 四、按名字推迟的十一个（理由不是"忘了"）

| 名字 | 为什么推迟 |
|---|---|
| `credentials` | 镜像的 shim 是一个**能用的 WebAuthn 实现**（R163 未结项） |
| `mediaDevices` | 需要 `getUserMedia` / `enumerateDevices` 表面才可信 |
| `serviceWorker` | 一个永不注册的 `navigator.serviceWorker` **本身就是破绽** |
| `storage` | 需要 `estimate()` 与 `persisted()` 的回答 |
| `wakeLock` | 需要 `request()` 返回带 `release()` 的哨兵 |
| `share` | 需要 `canShare` / `share` 一对，两者都可调用 |
| `canShare` | 与 `share` 成对 |
| `requestMediaKeySystemAccess` | 返回关于 key system 的 promise；一个直接 resolve 的桩是新的破绽 |
| `gpu` | WebGPU adapter 表面**本身就是指纹** |
| `clipboard` | 需要 read/write 表面 |
| `audioSession` | Safari 独有；在这里放桩等于给 Chrome 一个它从来没有的成员 |

## 五、27 个"引擎已有"的名字（缺的是值）

```
hardwareConcurrency  geolocation  mediaCapabilities  mediaSession  permissions
webdriver  maxTouchPoints  userActivation  cookieEnabled  appCodeName  appName
appVersion  platform  product  productSub  userAgent  vendor  vendorSub
language  languages  onLine  plugins  mimeTypes  pdfViewerEnabled
sendBeacon  getGamepads  javaEnabled
```

## 六、10 个继承来的

```
toString  toLocaleString  valueOf  hasOwnProperty  propertyIsEnumerable
isPrototypeOf  __defineGetter__  __defineSetter__  __lookupGetter__
```

## 七、怎么复算

普查来自**在本引擎里实测**，不是读文案：

```
python analysis\ida.py str "<名字>" --limit N    # 镜像里有没有这个键
```

引擎侧的存在性要在运行时探测（`Navigator.prototype` 上是否有该自有属性），本仓库不再用代码保存这份结果。

运行时里保留的对应物是 `NavigatorLocks.Installed`（`["standalone", "locks"]`）——**那是产品代码**。
