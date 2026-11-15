import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 每个 profile 一套指纹：镜像里的 `Fingerprint.template.json`（第 130 轮）

YG 指出原版有「不断生成新 Chrome profile」的机制，用来做出不同指纹，配合 Kasada token 与高并发。
**镜像里有完整的证据**，而且 replica 之前缺的正是这一半。

### 一、证据

一条元数据运行把 `Fingerprint` 类的字段列了出来：

```
<ColorDepth>k__BackingField            <DeviceMemory>k__BackingField
<HardwareConcurrency>k__BackingField   <PixelRatio>k__BackingField
<ScreenWidth>k__BackingField           <ScreenHeight>k__BackingField
<AvailableScreenWidth>k__BackingField  <AvailableScreenHeight>k__BackingField
```

旁边还有：

| 字面量 | 含义 |
|---|---|
| `Fingerprint.template.json` | **模板文件** —— 指纹不是随机的，是从模板填出来的 |
| `Fingerprint`（77 次） | 类/字段名 |
| `--profile-directory=`、`user-data-dir` | Chromium 开关 |
| `Profile 0` / `Profile 1` / `Profile 6` / `Profile 8` | **编号的 profile 目录** |
| `--window-size=363,684` | 一个实测窗口尺寸（偏窄，像真实小屏） |
| `set_ColorDepth` / `set_DeviceMemory` / `set_HardwareConcurrency` | 这些值是被**写进**浏览器的 |
| `x-kpsdk-v/-cd/-ct/-dt/-dv/-fc/-h/-im` | Kasada 的 8 个头 |

**结论：模板 → 每个 profile 一份指纹 → 每个 profile 一个 Chrome 身份 → 每个身份单独出 token。**

### 二、replica 之前的样子

```csharp
Object.defineProperty(N, 'hardwareConcurrency', { get: () => 8, configurable: true });
Object.defineProperty(N, 'deviceMemory', { get: () => 8, configurable: true });
```

**两个值所有 run 都一样**，而且六个 screen 字段**根本没设**。

> 指纹检查最先看的就是这个：**同一个安装里两个会话报告完全相同的硬件**，
> 比「没有伪装」更容易被识别 —— 因为真实用户不会这样。

### 三、这一轮做的

`BrowserFingerprint`（8 个字段，与镜像一致）：

- `ForProfile(key)` —— **按 profile key 确定性生成**：同一个 profile 永远同一套指纹
  （指纹在两次请求之间变化是比不伪装更大的破绽），不同 profile 拿到不同屏幕/硬件；
- `ToJavaScript()` —— 把 8 个字段全部注入（含 `screen.availWidth/availHeight`、`pixelDepth`、
  `devicePixelRatio`）；
- `ProfileDirectoryName(key)` —— `Profile 0..8`，与镜像的编号目录同形；
- `WindowSizeArgument()` —— 窗口尺寸跟着屏幕走，**不再固定 1280×900**（那和 1920×1080 的屏幕对不上）。

`ChromiumBridge` 现在：

```
var fingerprint = BrowserFingerprint.ForProfile(profile);
args: fingerprint.WindowSizeArgument(), fingerprint.ProfileDirectoryArgument(profile)
inject: StealthScript.Replace("__HC__", …).Replace("__DM__", …)
ApplyStealthAsync(…, BrowserFingerprint? fingerprint = null)   // 无 profile 时按 UA 派生
```

### 四、为什么「每个 profile 一套」比「每次随机」更强

| 做法 | 检测者看到 |
|---|---|
| 每次随机 | 同一账号两次请求硬件不同 → **明显异常** |
| 全部固定 | 所有账号硬件相同 → **农场特征** |
| **每 profile 一套、profile 内不变** | 像一群真实用户，各自一台机器 |

第三种才是原版的做法，也是 `Fingerprint.template.json` 存在的理由 —— 模板保证**多样性有边界**
（四个真实屏幕尺寸、四组硬件），不会随机出「1373 宽 / 1920 可用」这种自相矛盾的组合。

### 五、还没做的

- 模板文件本身没有从镜像里还原出来（只确认了文件名与字段集），现在是代码内置的四屏四档；
- `maxTouchPoints` 仍固定 0（桌面口径），镜像是否按 profile 变化未查证；
- 语音列表、WebGL vendor 这些已有伪装，但**没有跟随 profile 变化**。
'''

if "## 每个 profile 一套指纹" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("fingerprint section documented")
else:
    print("already present")
