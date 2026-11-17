# 10 · 移动构型（iOS / MFC / MobileDv）

> 前面几份讲的都是"桌面 Chrome 形态"。这份补的是**另一条正交的维度**：
> 同一个 Kasada 挑战，可以按**移动端**的样子去解 —— 而且原版对这件事有一整层专门的支持。
>
> 全部 [Obs]，地址由 `analysis/ida.py str` 得到。

---

## 1. 两个正交维度（这是理解"四种模式"的正确坐标系）

```
              执行者
          ┌──────────┬──────────┬──────────┐
设备形态   │  Jint    │  浏览器  │  服务商  │
──────────┼──────────┼──────────┼──────────┤
桌面 Chrome│  yes     │  yes     │  yes     │
iOS / 移动 │  (?)     │  yes     │  MFC     │
```

`KasadaStrategy` 的四模式（`Api`/`Local`/`Fallback`/`MobileFallback`）只描述了**执行者**这一维；
**设备形态是另一维**，它的词汇散落在别处：`IsMobile` / `MfcEnabled` / `MobileDv` / `GenRandomIos` / `SpoofMobile`。

**⇒ 移植时不要把它当成"第五种模式"** —— 它是与"用哪个执行者"独立的开关。

---

## 2. 移动侧的全部符号（[Obs]）

### 2.1 Kasada handler 上的三个开关

```
get_IsMobile / set_IsMobile         0x14345a7e8 / 0x14345a7f5
get_MfcEnabled / set_MfcEnabled     0x14345a802 / 0x14345a811
get_VersionProvider / set_...       0x14345a811 同族
<IsMobile> <MfcEnabled> <VersionProvider> k__BackingField   0x14345aaee
IsMobile                            0x14345ab59
```

这三个字段同时出现在 `KasadaMobileHandler`（`d__46`–`d__50`，比桌面版多一个 `GetMfc`）里 ——
**移动构型不是一个单独的实现类，而是同一套流程加了三个开关与一个阶段**（05 §1）。

`VersionProvider` 单独存在，说明**移动端的 `x-kpsdk-v` 版本号来源与桌面不同** —— 不能共用一个常量。

### 2.2 移动端的 dv

```
get_MobileDv@      0x14344855b
MobileDv           0x143448579
```

它就在 cd 那个类型里（`0x143448xxx` 片），与 `_kasadaDv` / `x-kpsdk-dv` 同族。

**⇒ `x-kpsdk-dv` 在移动构型下取的不是桌面那个值**，而是 `MobileDv`。
这也解释了为什么 01 §3.1 里 `dv` 的语义一直标 Unk：它有**两个来源**，取决于构型。

### 2.3 iOS 指纹生成

```
GenRandomIos       0x143448fbe     （同族：GenRandomChrome / GenRandomSizedBrowser / GetRandomWebGLRenderer / IsChrome）
```

**指纹生成器里有 "Ios" 这一个分支** —— 说明原版能产出 iOS 形态的浏览器指纹，
不是"把 Chrome 的 UA 换成 iPhone 就算移动"。

### 2.4 浏览器侧的移动模拟参数

```
get_SpoofMobile / set_SpoofMobile        0x1433048fd / 0x14330490d
get_MobileUserAgent / set_MobileUserAgent   0x14330662f 同族
MobileViewportWidth                      0x143306b6e
MobileViewportHeight                     0x143306b87
MobileWindowHeight                       0x143306ba6
MobileUserAgent                          0x143306ee6
```

这五个是**给浏览器路用的**：伪造移动 UA、把视口改成手机尺寸、把窗口高度改成手机高度。
`SpoofMobile` 是总开关。

---

## 3. MFC 是什么（按现有证据能说到哪一步）

| 证据 | 结论 |
|---|---|
| `Getting Kasada (MFC)` `0x146da1804` 属 **getting** 家族 | MFC 是 **Api 路**上的一个变体，不是 solving 的 |
| `GetMfc`（`d__49`）只在 `KasadaMobileHandler` 那套里 | 只有移动 handler 有这个阶段 |
| `MfcEnabled` 是**可配置开关** | 用户可以关掉它 |
| `MFC` 的展开 | **[Unk]** —— Mobile Flow/Fingerprint Challenge 都可能 |

**⇒ 最小的诚实表述**：MFC = 「在移动构型下，向服务商要一个移动形态的 token」。
它不是一条独立的路，是 `Api` 路在 `IsMobile` 时的分支。

---

## 4. 移植时的清单

```
[ ] 把"执行者"与"设备形态"当两个独立开关，不要合并成一个枚举
[ ] 移动构型下：x-kpsdk-dv 取 MobileDv，x-kpsdk-v 由 VersionProvider 给（不要复用桌面的版本常量）
[ ] 浏览器路要移动化时，四个参数一起改：UA / 视口宽 / 视口高 / 窗口高（只改 UA 会被看出来）
[ ] 指纹生成要选 iOS 分支，不是"桌面指纹 + iPhone UA"
[ ] MFC 只在 Api 路 + 移动构型时出现；其它组合下这个开关应当无效
```

---

## 5. 复算

```powershell
python analysis\ida.py str MobileDv        --limit 5    # total = 2
python analysis\ida.py str GenRandomIos    --limit 5    # total = 1
python analysis\ida.py str IsMobile        --limit 10   # total = 6
python analysis\ida.py str SpoofMobile     --limit 5
python analysis\ida.py str MobileViewport  --limit 5
python analysis\ida.py str MfcEnabled      --limit 5
```
