### 76 个类型原版有、replica 没有 —— 分类之后只剩 5 个真缺口

IDA MCP 在这台机器上起不来（proxy 未 spawn、无实例、端口全 REFUSED），所以这一轮改用
**已有的 1100 万字符字符串表**做类型对比。

### 方法

反射元数据在 NativeAOT 镜像里以 `Namespace.Type,Cybersole.Member!Kind` 的形式出现，
所以 `([A-Z]\w*(?:\.[A-Z]\w*)+),Cybersole\.\w+!` 是一个可靠的类型声明判据。

```
原版类型: 205
replica 类型: 374
原版有、replica 没有: 76
```

### 分类之后

| 桶 | 类型数 | 元数据引用 | 是缺口吗 |
|---|---|---|---|
| localization | 5 | 20 | **✅ 真的** |
| modal-window | 10 | 76 | 部分（replica 用独立 Window） |
| list-row / cell | 21 | 83 | 部分（内联构造） |
| grid / list view | 20 | 162 | **否** |
| custom control | 3 | 8 | 部分 |
| unbucketed | 17 | 部分 | 名字不同（`CustomBrowser` vs `CustomBrowserWindow`） |

**「grid / list view」那 20 个 162 次引用看着最吓人**（`ProxyView` 41 次、
`SettingsView` 39 次、`AccountGrid` 28 次），**但它们不是缺口**：

replica 把同一批页面建在 `MainWindow.BuildProxies()` / `BuildSettings()` 这样的方法里，
一个类换成了几个方法。**函数数量对等不等于类型数量对等。**

### 唯一的真缺口：本地化

原版有：

```
Cybersole.Ui.Localization.LocalizationService
LocalizeFormatExtension     Value / Value2
LocalizeSwitchExtension     Condition
LocalizeEnumExtension       Value
LocalizeFallbackExtension   Value
Cybersole.Ui.Views.Settings.LocalizedOption   Text / Value
Cybersole.Global.Settings.Language
```

**继续挖之后发现规模比想象的**小**得多**：

字符串表里**只有四个本地化资源键**：

```
"Language.ChineseSimplified": "Chinese (Simplified)"
"Language.English":           "English"
"Language.Japanese":          "Japanese"
"Language.Korean":            "Korean"
```

**镜像里那 110 个 `locales/*.pak` 是打包进去的 Chromium 的，不是这个应用的。**

所以原版**只本地化语言选择器自己的四个选项**，其余 UI 全是英文。
5 个 `Localize*` 标记扩展是用来把「选中的语言」渲染成人类可读名字的，不是翻译引擎。

### 修

新增 `Cybersole.Services.Localization.LocalizationService`（对应原版的类名）：

```csharp
public static readonly IReadOnlyList<(string Key, string Display)> Languages = new[]
{
    ("Language.English", "English"),
    ("Language.Japanese", "Japanese"),
    ("Language.ChineseSimplified", "Chinese (Simplified)"),
    ("Language.Korean", "Korean"),
};
```

`DisplayOf` 接受三种写法（`Language.English` / `English` / 裸词）——因为旧 settings 存的是
`"English"` 而资源键是 `"Language.English"`。

`Settings → General → Language` 从**自由文本输入框**换成**四选下拉**：

```csharp
var languageSvc = new Cybersole.Services.Localization.LocalizationService(s);
var language = UiKit.Combo(
    Cybersole.Services.Localization.LocalizationService.DisplayNames.ToList(),
    languageSvc.CurrentIndex);
```

### 一个顺手修掉的问题

第一次插入时我把 `services.Config.Save()` 放在了 `languageSvc.Select(...)` 之后、
其它字段赋值之前——**那次 Save 会写一个只更新了一半的状态**，方法末尾还有第二次 Save。

删掉中间那次。**这是 R122「后写赢」的近亲：中间保存不是错，是多余且有害。**

### 实测

| 操作 | 结果 |
|---|---|
| 打开 `Settings → General` | `Language` 是下拉框，显示 **English** ✅ |
| 展开 | `Japanese` 在列表里 ✅ |
| 选 `Japanese` → `Save` | 下拉框显示 **Japanese** ✅ |
| 读 `settings.json` | `"language": "Japanese"` ✅ |

### 不做的部分

**给整个 UI 加翻译表**。

原版没有，做了就是**凭空造出原版不存在的行为**——这违反「1:1」的定义本身。

> **对等的边界是「原版有什么」，不是「听起来应该有什么」。**

### 验证

```
dotnet test      583 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    language 已恢复 English
```

---
