# 裁决记录：LicenseControl 属登录凭证功能，不做复刻（YG，2026-11-16）

> 本项目复刻 Cybersole 的**业务功能**（任务/账号/代理/分析/设置等页面与流程）。
> 登录凭证类功能（账号登录、许可选择/激活、LicenseControl/AuthWindow/LoginControl 一族）
> 只用于管理用户，**不属于复刻范围**。

## 裁决原文（R702，YG）

> 「LicenseControl是登陆凭证功能吗，本项目主要用于复刻cybersole的功能，登陆凭证功能只是
> 用来管理用户的不需要做，这点可以写进项目记忆」

## 对判据 (a) 的直接后果

`LicenseControl.Authenticate` 此前是 17 条类型缺失里唯一的 **UNIMPLEMENTED（真缺）**。
按本裁决，它不是"能做而没做"，而是**范围外**——判据 (a) 的括号允许「不可得 → 写明原因」，
这条的原因从今天起是：**登录凭证功能，裁决不做**。

同理适用于同族条目：

| 条目 | 原判定 | 现处置 |
|---|---|---|
| `Ui.Views.Auth.LicenseControl`（Authenticate/Dashboard/Refresh） | UNIMPLEMENTED | **范围外（本裁决）** |
| `Ui.Views.Auth.AuthWindow`（Exit/Logout/Minimise） | UNKNOWN (non-discriminating) | **范围外（同族，登录窗口壳）** |
| `Ui.Views.Auth.LoginControl` | （已实现，R213） | 保留现状，不再投入 |

## 证据副产品（保留，不因裁决作废）

R702 的定位链证明了**第三种定位法**（冻结字符串 → rip-relative disp32 → 调用点 → 反编译），
LicenseControl 全簇地址与 `sub_140765730` 的 2387 行反编译已落盘：

- `analysis/license_control_main.c` + `license_refs_resolved.txt`
- `analysis/disp32_scan.py` / `disp32_scan_any.py` / `site_to_func.py` / `names_at.py`

这些是**方法资产**，对范围内的功能同样可用（本轮已用它解开 (b)，见 BLOCKERS §134）。
