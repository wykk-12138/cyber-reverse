### 四个完整翻译字典：1142 个键 × 4 种语言

R126 的结论是错的，这轮改正。

### R126 错在哪

R126 用 `"Language\.[A-Za-z]+"\s*:\s*"([^"]*)"` 扫字符串表，只找到 4 个键，于是判断「原版只本地化语言名」。
**但那个搜索找的是资源清单，不是资源内容。**

R130 读命名空间清单时看到 `Cybersole.Core` 有 22 个 embedded resource，其中四个是
`Cybersole.Locales.{en,ja,ko,zh-Hans}.json`。R131 把它们切出来了：

```
slice 0  0x3c4ec34..0x3c5e2e6   63154 B  1142 keys
slice 1  0x3c5e2e6..0x3c7026d   73607 B  1142 keys
slice 2  0x3c7026d..0x3c8109e   69169 B  1142 keys
slice 3  0x3c8109e..0x3c9052e   62608 B  1142 keys
```

**每个 1142 个键，键集完全一致。**

### 命名：第一次搞错了判据

我用 `Language.Japanese` 的值当判别符，得到：

```
slice 0: 'Japanese'  → ja     ← 错，这是 en
slice 1: '日本語'    → unknown
slice 2: '일본어'    → unknown
slice 3: '日语'      → unknown
```

**问题**：`Language.Japanese` 的值**本身是被翻译的**，所以英文文件里它是 `"Japanese"`。

**正确的判别符还是 `Language.Japanese`**，只是要按四种可能的取值映射：

```python
BY_JP = {'Japanese': 'en', '日本語': 'ja', '일본어': 'ko', '日语': 'zh-Hans'}
```

`Language.English` 不行——日语文件里它也是 `'English'`（外来词）。

### 内容

```
en       Save / Cancel / Delete
ja       保存 / キャンセル / 削除
ko       저장 / 취소 / 삭제
zh-Hans  保存 / 取消 / 删除
```

**真的翻译，覆盖 Analytics / Common / Tasks / Proxies / Settings 全部 1142 个 UI 字符串。**

### 一个 MSBuild 陷阱：`.en.` 被当成文化标识

资源加进 `Cybersole.Core.csproj` 之后，`GetManifestResourceStream` **拿不到**。

查 `obj/` 目录：

```
obj\Debug\net8.0\en\Cybersole.Core.resources.dll
obj\Debug\net8.0\ja\Cybersole.Core.resources.dll
obj\Debug\net8.0\ko\Cybersole.Core.resources.dll
obj\Debug\net8.0\zh-Hans\Cybersole.Core.resources.dll
```

**MSBuild 看到文件名里的 `.en.` / `.ja.` / `.ko.`，把它们当成文化标记，拆成了卫星程序集。**
主 dll 里什么都没有，`manifest.GetManifestResourceStream("Cybersole.Locales.en.json")` 返回 null。

**修**：

```xml
<EmbeddedResource Include="Locales\Cybersole.Locales.en.json"
                  LogicalName="Cybersole.Locales.en.json" WithCulture="false" />
```

**实测**：`Cybersole.Core.dll` 从 **119 KB → 387 KB**，卫星目录消失，`en=True zh=True`。

> **一个叫 `X.en.json` 的资源文件，默认行为是变成 `en/X.resources.dll`。** 名字里的文化标记是隐式的。

### 第二层：`Assembly` 取错

`LocalizationService` 在 `Cybersole.Services`，资源在 `Cybersole.Core`。
`typeof(LocalizationService).Assembly` 找的是 Services，自然是空的。

改成 `typeof(GlobalSettings).Assembly`。

### 第三层：测试抓到了自己的假阳性

`SourceEncodingTests` 红了 18 处：

```
Cybersole.Locales.zh-Hans.json:40  确定吗?
Cybersole.Locales.zh-Hans.json:81  有账户?
Cybersole.Locales.zh-Hans.json:115 要帮助?
```

**这些是正确的简体中文 UI 文本**，`?` 是句末问号。

**R112 的判据是 `[\u4e00-\u9fff]{1,3}[\ufffd?]`** —— 「CJK 字符后跟问号」。
**那个判据只在全库没有真中文时才是绿的。** R131 一加入真中文，它立刻误报。

**它检查的东西和它想检查的东西，从来不是一回事。**

R112 实际找到的是三个特定序列（U+9225 / U+922B / U+95B3 后跟 `?`），收紧到那三个：

```csharp
new(@"\u9225\?|\u922b\?|\u95b3\?|\ufffd", RegexOptions.Compiled)
```

**第一次改还写错了**：`\u9225?` 里的 `?` 是**正则量词**（0 或 1 次），所以整个模式匹配空字符串，
报出 **2,423,427 处命中**。加 `\?` 转义才对。

### 实测

| 操作 | 结果 |
|---|---|
| 展开 `Language` 下拉 | `Chinese (Simplified)` 在列表里 ✅ |
| 选它 → `Save` | 下拉框显示 `Chinese (Simplified)` ✅ |
| 读 `settings.json` | `"language": "Chinese (Simplified)"` ✅ |

### 八条测试

| 测试 | 断言 |
|---|---|
| `AllFourResourcesAreEmbedded` | 4 个资源名都在 |
| `EveryDictionaryHasTheSameKeyCount` | 每个 1142 |
| `EveryDictionaryCoversTheSameKeys` | 键集完全一致 |
| `TranslationsDifferFromEnglish` | 四份英文副本会被抓住 |
| `ScriptIsCorrectForEachLanguage` | ja 有假名/汉字、ko 有谚文、zh 有汉字 |
| `UnknownKeyFallsBackToItself` | 缺失的键渲染成键名，不是空白 |
| `TagResolutionAcceptsEveryStoredForm` | 9 种存储写法都能解析 |

**`ScriptIsCorrectForEachLanguage` 是最强的一条**：它不检查「和英文不一样」，
而是检查「**是那种文字**」。四份拷贝英文能过前面所有条，过不了这条。

### 验证

```
dotnet test      606 通过 / 0 失败 / 2 跳过   (+15)
live contracts   PASS
store modules    PASS 61 registered
Cybersole.Core.dll  119 KB → 387 KB
settings.json    language 已恢复 English
```

---
