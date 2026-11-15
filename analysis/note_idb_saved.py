import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

anchor = "**下一步的功能工作**："
add = (
    "**IDA 数据库（重启前已保存）**：\n"
    "`target\\Cybersole.exe.i64` —— **1375 MB，2026-11-13 09:28:18**（由 `idb_save` 打包生成）。\n"
    "保存走的是 **HTTP 直连插件**，不是 GUI：\n"
    "`POST http://127.0.0.1:13337/mcp`，JSON-RPC `tools/call` → `idb_save`；`server_health` 回报\n"
    "`status: ok`、`auto_analysis_ready: true`、`hexrays_ready: true`、`imagebase: 0x140000000`。\n"
    "**教训**：IDA 有模态框时插件 `tools/call` 会一直超时（`tools/list` 仍秒回）—— 先关模态再调。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "IDA 数据库（重启前已保存）" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("IDB save note inserted")
