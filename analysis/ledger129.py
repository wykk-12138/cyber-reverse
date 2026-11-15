import io, os, re, subprocess, sys

REPLICA = r"D:\projects\cyber-reverse\replica"
TOOL = os.path.join(REPLICA, "tools", "endpoint-provenance.py")
DOC = os.path.join(REPLICA, "docs", "ENDPOINT_PROVENANCE.md")

# Classes, in the words the document uses.
LIVE = {
    # answered a real request during this session (recorded in VERDICT / ENDPOINT_FAMILIES)
    "/api/beast": "R91: the prefix answers (geoIP and monetate live under it)",
}
FIXTURES = {
    # deliberately-absent paths kept so a test can forbid them
    "/api/cart/add": "PopMartEndpoints.Invented — negative fixture (R100)",
    "/api/order/submit": "PopMartEndpoints.Invented — negative fixture (R100)",
    "/api/stock": "PopMartEndpoints.Invented — negative fixture (R100)",
}

out = subprocess.run([sys.executable, TOOL], cwd=REPLICA, capture_output=True, text=True,
                     encoding="utf-8", errors="replace")
lines = (out.stdout or "").splitlines()

consts = next((l for l in lines if l.startswith("endpoint constants:")), "?")
inline_total = next((l for l in lines if l.startswith("inline URL/path literals:")), "?")

rows = []
for line in lines:
    m = re.match(r"\s+INLINE-INVENTED\s+(\S+)\s+:(\d+)\s+(\S+)\s*$", line)
    if m:
        rows.append((m.group(1), int(m.group(2)), m.group(3)))

unknown = [r for r in rows if r[2] not in LIVE and r[2] not in FIXTURES]

doc = io.StringIO()
doc.write("# 端点溯源台账\n\n")
doc.write("第 129 轮生成。每个在 `src/Cybersole.Stores/Flows/*.cs` 里出现的 URL / 路径字面量，\n")
doc.write("要么**逐字出现在镜像里**，要么在下面登记为 `live`（有真实响应证据）或 `fixture`\n")
doc.write("（故意保留的不存在路径，用测试禁止）。**三者都不是的，就是发明。**\n\n")
doc.write("```\n%s\n%s\n```\n\n" % (consts, inline_total))
doc.write("## live —— 有响应证据、但镜像里没有这条字面量\n\n")
for path, why in sorted(LIVE.items()):
    doc.write("- `live` `%s` —— %s\n" % (path, why))
doc.write("\n## fixture —— 故意保留的不存在路径\n\n")
for path, why in sorted(FIXTURES.items()):
    doc.write("- `fixture` `%s` —— %s\n" % (path, why))
doc.write("\n## 待定 —— 既不在镜像里，也没有响应证据（%d 条）\n\n" % len(unknown))
doc.write("| 文件 | 行 | 字面量 |\n|---|---|---|\n")
for name, line, value in unknown:
    doc.write("| `%s` | %d | `%s` |\n" % (name, line, value))
doc.write("\n**这 %d 条就是要处理的清单**：要么去镜像里找到真的那条，要么改成 `live` 并补证据，\n"
          "要么删掉并把功能标成未实现。\n" % len(unknown))

io.open(DOC, "w", encoding="utf-8", newline="").write(doc.getvalue())
print("wrote", DOC)
print("unknown:", len(unknown), "live:", len(LIVE), "fixtures:", len(FIXTURES))
