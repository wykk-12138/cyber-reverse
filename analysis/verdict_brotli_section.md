### `BrotliDictionary`：从单文件镜像里切出 122,784 字节的标准字典

`bucket_cybersole_ns.txt` 的命名空间清单里，`Cybersole.Http` 有 8 个子命名空间，replica 只有 2 个。
逐个查过之后，每个子命名空间只有 1–2 个类型：

| 原版 | replica |
|---|---|
| `Compression.BrotliDictionary` | **缺** |
| `Content.IBody` | 缺 |
| `Net.IMeasuredDialer` | 缺 |
| `X509.RootCertificates` | 缺 |
| `Analytics` / `Debug` | 有（R127 修过 `Flush`） |
| `Newtonsoft` | 用 Newtonsoft 包 |

**前四个是抽象层**（接口/证书库/字典），不是功能模块。其中只有一个能真正验证：
`BrotliDictionary`，因为它在程序集清单里是一个**具名资源**。

### 定位

```
line 179772: Cybersole.Http, Version=0.10.0.0, Culture=neutral, PublicKeyToken=null
             ^Cybersole.Http.Compression.BrotliDictionary.bin
```

`Cybersole.Http.dll` 不在安装目录（只有 Skia/HarfBuzz/ANGLE 三个原生库），
所以资源打包在 123 MB 的单文件里。

资源名后面紧跟的是**下一个程序集清单条目**，说明数据不在那里。换判据：
**RFC 7932 规定这个字典恰好 122,784 字节**，所以搜这个长度字段。

```python
struct.pack('<Q', 122784)   →  1 occurrence at 0x62dd580
```

从 `0x62dd580 + 8` 切出 122,784 字节：

```
head ascii: @.,F..... ., . of the . of .s ... and . in .". to .">.... .]. fo
```

**` of the `、` and `、` in ` —— 正是 RFC 7932 的前缀表。**
长度精确匹配 + 内容形态匹配 = **证据等级 A**。

### 加进 replica

`src/Cybersole.Http/Compression/BrotliDictionary.bin`（122,784 字节），
csproj 里用**原版同一个资源名**：

```xml
<EmbeddedResource Include="Compression\BrotliDictionary.bin"
                  LogicalName="Cybersole.Http.Compression.BrotliDictionary.bin" />
```

`BrotliDictionary.cs` 提供 `Bytes` / `Length` / `IsAvailable` / `AvailableResources()`。

**编译产物从 ~60 KB 涨到 281 KB** —— 资源确实进去了。

### 四条测试

| 测试 | 断言 | 输出 |
|---|---|---|
| `ResourceIsEmbedded` | 资源名存在 | `Cybersole.Http.Compression.BrotliDictionary.bin` |
| `LengthMatchesRfc7932` | 恰好 122,784 | `length: 122784` |
| `OpeningBytesAreThePrefixTable` | 首 64 字节 ≥30 可打印且含 `of the` | `printable in first 64: 43` |
| `BytesCoverTheWholeByteRange` | 256 个不同字节值 | `distinct byte values: 256` |

**第三条是核心**：它不检查「长度对不对」，而检查「**内容是不是那个东西**」。
一个 122,784 字节的随机 blob 能过第二条，过不了第三条。

### 诚实的限制

**字节有了，但解压还用不上。**

用这个字典压出来的 Brotli 流只能用这个字典读，而 .NET 8 的
`BrotliDecoder` / `BrotliStream` **不暴露字典参数**。

**要真读这种响应，得写一个完整的带字典 Brotli 解码器**——那是几百行的活，不在这一轮。

所以在 `BrotliDictionary` 的文档注释里写清了：

> Reading such a body would need a full decoder with dictionary support. What this type provides
> today is parity of the resource and of its accessor, which is what the ledger can actually check.

**这不是「做了一半」，是「做到了能验证的那一半，并且说明了另一半为什么不在」**。

### 另外三个抽象层：不补

`IBody` / `IMeasuredDialer` / `RootCertificates` 只有**接口名**，没有任何成员或实现被反射引用。
按 R90 的标准，**证据等级 C，不足以凭空建一个接口**——建出来只能是我的想象，而且会让
「对等」这个说法变得更不可信。

### 验证

```
dotnet test      591 通过 / 0 失败 / 2 跳过   (+4)
live contracts   PASS
store modules    PASS 61 registered
build errors     0
Cybersole.Http.dll  60 KB → 281 KB
```

---
