### `--eval-file` 造好了：脚本从文件读，不进命令行

上一轮想用 `--steps eval:<js>` 做探测，失败在**两层 Shell 转义**上：

1. `--steps` 用 `;` 分隔步骤，而 JavaScript 里全是 `;` —— 脚本被切碎
   （改成 `;;` 分隔，但还有第二层）
2. PowerShell 传 `--steps="...'...'..."` 时把引号吃掉了 —— 报 `SyntaxError`

解法不是继续跟转义较劲，而是**别把 JS 放命令行**：

```
--eval-file=<path>    从文件读 JavaScript 执行
```

一次就通了。

```
--- eval-file C:\...\bstn_card_probe.js (1125 chars) ---
{"cards":61,"withLink":2,"hrefs":[...],"clickable":null}
```

### BSTN 商品卡的探测结果

```json
{
  "cards": 61,
  "withLink": 2,
  "hrefs": ["https://www.bstn.com/us_en/men", "https://www.bstn.com/us_en/men"],
  "clickable": null
}
```

**61 个商品卡，只有 2 个含 `<a href>`，而且两个都是导航链接，不是商品链接。**

这解释了为什么 `--follow` 走三层 940 个链接也找不到商品页：

> **BSTN 的商品链接不写在 DOM 的 href 里。** 商品卡是 `<div class="flex flex-col gap-[5px]">`，
> 导航靠 JS 事件。

`clickable: null` 是因为我的探针脚本判断写错了（`withLink === 0` 才点，
但实际有 2 个导航链接所以没进那个分支）——**这是探针的 bug，不是站点的行为**。

### 工具链现在的完整形态

```
NetworkCapture <url> [seconds]
                 [--headless]
                 [--scroll]                               懒加载网格
                 [--find-add]                             列出加购控件
                 [--click=<css>]                          点一次
                 [--steps="a;;b;;c"]                      串联动作（;; 分隔）
                 [--follow=<n>]                           递归下钻列表层
                 [--eval-file=<path>]                     执行脚本文件
```

七次迭代，每次都是因为上一次不够用。

### 一条反复应验的规律

| 轮次 | 卡在哪 | 真正的解法 |
|---|---|---|
| R51 | HBX 页面 0 个按钮 | 加 `--scroll` |
| R52 | 加购按钮点了没反应 | `--steps` 先选尺码 |
| R53 | BSTN 商品页找不到 | `--follow` 下钻 |
| R54 | 下钻三层还是没有 | 商品链接不在 href 里 |
| **R55** | **JS 传不进命令行** | **`--eval-file`** |

**五次里有四次是"工具不够"，只有一次是"站点行为如此"。**

这说明在陌生站点上做自动化，**工具能力的上限决定了能看到什么**。
用 `--find-add` 看不到没渲染的按钮，用 `--follow` 看不到 JS 路由的链接。

### 下一步

修那个探针 bug（判断"有没有**商品**链接"而不是"有没有链接"），然后：
点商品卡 → 读 `location.href` → 拿到商品 URL → 用 `--steps` 选尺码加购。

**同一套打法对 `goat` 也适用**——它同样是 JS 路由，同样卡在入口。

---
