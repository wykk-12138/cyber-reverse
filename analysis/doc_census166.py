import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 五十个名字的户口普查：27 / 10 / 13（第 166 轮）

上一轮量出「28/50 在原型上」。这一轮问清另外二十二个在哪儿 —— 答案把整个问题切成两半。

```
在 Navigator.prototype    27   引擎有；只需值，不需存在
在 Object.prototype       10   toString / valueOf / hasOwnProperty / __defineGetter__ … 继承来的
完全不存在                13   手机有、本引擎没有
```

### 一、第三行是 `NavPrune` 的镜像

| 方向 | 名单 | 动作 |
|---|---|---|
| 引擎**有**、手机**没有** | `userAgentData` `connection` `bluetooth` `usb` `hid` `serial` `xr` `getBattery` `deviceMemory` | **删** |
| 手机**有**、引擎**没有** | `standalone` `locks` `credentials` `mediaDevices` `serviceWorker` `storage` `wakeLock` `share` `canShare` `requestMediaKeySystemAccess` `gpu` `clipboard` `audioSession` | **装** |

> **这是同一次测量的两个读法。**

### 二、十三个里这一轮只装两个

`standalone`（布尔）与 `locks`（页面会调方法的对象）—— 这两个是**普通值**，装上去不会引出更多问题。

其余十一个**逐个写下理由**，最重的是 `credentials`：

```
credentials   the image's shim is a working WebAuthn implementation (R163 open item)
serviceWorker a navigator.serviceWorker that never registers is itself a tell
gpu           WebGPU adapter surface is a fingerprint of its own
audioSession  Safari-only; a stub here would be a member Chrome never had either
```

**「先不装」和「忘了装」是两件事** —— 前者必须能说出为什么。

### 三、这一轮的一句话

> 一直以为「补上手机该有的成员」是一张清单。这一轮才发现它是**两张**：一张删、一张装，
> 而且两张来自同一次测量。
>
> **把一个负数说清楚，和把一个正数说清楚，价值一样。**
'''

if "## 五十个名字的户口普查" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("census documented")
else:
    print("already present")
