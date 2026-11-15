# 从原版二进制字节直接取 locale 键（生成文件，请勿手改）

> 由 `python analysis/locale_from_binary.py` 生成。**第三条路径**：现有三个文案工具都读
> `analysis/pe_strings.txt`，如果那份转储不完整，它们会一起错。这里直接扫 `target/Cybersole.exe`。

| 项 | 值 |
|---|---|
| 二进制大小 | 129243216 bytes |
| 二进制里的 locale 键 | **1142** |
| `pe_strings.txt` 里的 locale 键 | 1141 |
| 复刻件 4 个 locale 文件的键（并集） | 1142 |

  - `Cybersole.Locales.en.json`: 1142 键
  - `Cybersole.Locales.ja.json`: 1142 键
  - `Cybersole.Locales.ko.json`: 1142 键
  - `Cybersole.Locales.zh-Hans.json`: 1142 键

## 三种不对称

### 1. 二进制有、池里没有（池不完整 → 现有文案工具共同盲区）：1

- `TaskGroups.Order.A-Z`

### 2. 二进制有、复刻件没有（真实文案缺口）：0


### 3. 复刻件有、二进制没有（复刻件自己造的键）：0


