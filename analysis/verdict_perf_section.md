### 效率这条的完整数据

**真实网络**（`https://www.nike.com/`，`Speed=Slow`）。

最早的 12 样本跑分，池化**之前**：

```
SChannel   n=12  p50=424ms  p95=520ms
OwnTls     n=12  p50=390ms  p95=586ms
p50 ratio (own/system) = 0.92x
```

池化**之后**，12 样本：

```
SChannel   n=12  p50=432ms  p95=824ms
OwnTls     n=12  p50=432ms  p95=665ms
p50 ratio (own/system) = 1.00x
```

这两次的外部网络条件不同（SChannel 自己的 p95 从 520 涨到 824），而且
**12 样本的 p95 就是第 12 个值**——一个慢请求就能决定它。

### 扩到 50 样本后的结论（这是现在采用的数字）

池化后，`n=50`：

```
SChannel   n=50  p50=415ms  p95=588ms  min=342  max=892
OwnTls     n=50  p50=418ms  p95=693ms  min=367  max=933
p50 ratio (own/system) = 1.01x
p95 ratio (own/system) = 1.18x
```

**50 样本让 p95 变成第 48 个值**，不再被单个离群点决定。

| 指标 | 比值 | 判断 |
|---|---|---|
| p50 | **1.01x** | 几乎相同 |
| p95 | **1.18x** | OwnTls 慢 18% |
| min | 1.07x | 相近 |
| max | 1.05x | 相近 |

**p95 那 18% 是真实的，不是噪声。** 但 1.01x / 1.18x 都在"同量级"范围内——
用户的标准是"效率要相近"，不是"要更快或一样快"。

样本数可以用 `CYBERSOLE_PERF_SAMPLES` 覆盖（默认 50，最小 5）。

### 池化解决了什么

之前 p95 的劣势来自**每次请求都完整握手**——`NetClient` 每条请求都
`Tls12Client.ConnectAsync`，而一次结账要打十几次同一台主机。

`Tls12Pool` 把它补上了：按 `host:port:profile:ja3Hash` 做键，45 秒过期，
出错即丢弃（因为记录序号已不可信）。

**loopback**（无 TLS，仅 HTTP 链）：p50 0.18ms vs 0.19ms = **0.94x**
