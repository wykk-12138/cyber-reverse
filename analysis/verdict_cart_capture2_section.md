### 加购抓包：找到了按钮，但点击没触发请求

`NetworkCapture` 加了两个参数：

```
--find-add          列出页面上像"加入购物车"的控件，含 class / data-* 属性
--click=<css>       点击一个元素，等 5 秒，抓它触发的请求
```

### 一次关键的教训：`--scroll` 是必需的

同一个 HBX 商品页，两次 `--find-add` 的结果：

| 命令 | `totalButtons` |
|---|---|
| `--find-add`（不滚动） | **0** |
| `--scroll --find-add` | **518** |

**没滚动时页面里一个按钮都没有，滚动后才渲染出来。**

上一轮我根据 `totalButtons: 0` 得出"HBX 购买区不是 `<button>`"的结论——**那个结论是错的**，
真实原因是页面还没渲染完。

这是"数据不在这份输入里"的第四种表现：**不是输入内容不对，是输入还没到**。

### 找到的控件

```json
{"tag":"button","text":"Add to Bag","cls":"atc-button primary atc-mt"}
{"tag":"button","text":"Add to Bag","cls":"atc-button primary"}
{"tag":"button","text":"Add to Wishlist","cls":"wishlist-icon ..."}
```

加购按钮的 class 是 **`atc-button`**。

### 但点击没触发加购

```
--- click: clicked ---
（之后只有 analytics、AWS WAF、GA 事件）
```

`button.atc-button` 确实被点到了（返回 `clicked`），但没有发出任何购物车请求。

**最可能的解释：尺码未选，按钮是软禁用状态**（`disabled: false` 但点击被 JS 忽略）。

### 现在的状态

| 项 | 状态 |
|---|---|
| 加购按钮选择器 | ✅ `button.atc-button` |
| 前置条件 | ❌ 需先选尺码 |
| 购物车端点 | ❌ 仍未拿到 |

**下一步**：先执行一段 JS 选中第一个尺码，再点加购。
`--click` 目前只接受一个选择器，需要扩展成"一串动作"。

### 这一轮真正的产出

**工具**：`--find-add`（含宽选择器）和 `--click`。

**一个被推翻的结论**：`totalButtons: 0` 不等于"页面没有按钮"，可能只是"还没渲染"。

**一个被确认的假设**：加购按钮在尺码选择之后才可用。

---
