# Payload 覆盖表（从 `replica/src` 迁出，R1271）

原先在 `replica/src/Cybersole.Stores/Scripts/PayloadCoverage.cs`。按 `AGENTS.md` §3 的红线，
**覆盖表归 `docs/`，产品代码只放运行时逻辑**。表搬到这里；其中真正属于运行时的**一条规则**留在了
`SessionPayload.IsReadOnly` / `SessionPayload.StealthRule`。

## 一、已经答过的（复刻件早于该轮就有）

```
navigator.userAgentData.brands
navigator.userAgentData.mobile
navigator.userAgentData.platform
navigator.userAgent
navigator.platform
navigator.language
navigator.hardwareConcurrency
navigator.deviceMemory
webdriver_detect
```

## 二、该轮补上的

```
navigator.connection.effectiveType
navigator.connection.rtt
navigator.connection.saveData
navigator.connection.downlink
navigator.plugins
navigator.automationEnabled
screen.darkMode.enabled
```

> 连接四元组在运行时里的对应物是 `SessionPayload.ConnectionKeys`——**那一份是产品代码**，这里只是覆盖记账。

## 三、**装不了**的（检测方从页面自己算）

```
canvas-print-100-999
canvas-print-detailed-100-999
canvas_spoofing
js-errors
font-*
```

`canvas_spoofing` 与 `js-errors` 是**镜像自己的记账**，和它们描述的读数放在同一个命名空间里。

## 四、样本里的连接值（记录它，安装才不是猜）

| 键 | 值 |
|---|---|
| `effectiveType` | `4g` |
| `rtt` | `50` |
| `saveData` | `false` |
| `downlink` | `10` |

## 五、这条覆盖表存在要守的那条规则

> 一个 canvas 哈希是**跑 canvas 跑出来的结果**，不是一个可以覆盖的属性；
> 声称能装它的隐身层，是在夸大自己的射程。

运行时判定在 `SessionPayload.IsReadOnly`，句子在 `SessionPayload.StealthRule`。
`SurfaceRuntimeTests` 直接断言 `SessionPayload.IsReadOnly("canvas-print-100-999")` 为真。

## 六、怎么复算

```
python tools\where_is.py <成员名>
```

`implementation` 组里出现 ⇒ 有实现；只在 `analysis`/`doc` 里出现 ⇒ 只提名。
