"""Append the two plugin-tool confirmations to the R691 record and commit."""

import io
import subprocess

BLOCKERS = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"

ADD = """

### 六半、再加两个专用工具的复核（共五次独立确认）

| 工具 | 目标 | 结果 |
|---|---|---|
| `find_xref_signatures` | 国家码表 `0x1437D4BC4` | `total_xrefs: 0`, `signatures: []` |
| `trace_data_flow` (backward) | 裸键 `0x146e4d1c4` | `depth_reached: 0`, `edges: []` |
| `trace_data_flow` (backward) | 表地址 `0x1437D4BC4` | `depth_reached: 0`, `edges: []` |

两个节点在 IDB 里都只是 `db 50h ; P` / `db 63h ; c` 这样的**原始数据字节**，`func: null`、`name: null`。

**五次独立探测、五种不同机制，结论一致：这片数据在原版里没有任何可见的入边。**
"""


def main():
    body = io.open(BLOCKERS, encoding="utf-8").read()
    if "六半" in body:
        print("already appended")
    else:
        anchor = "### 七、仍然 Unknown"
        i = body.find(anchor, body.find("## 124."))
        if i < 0:
            print("MISS anchor")
            return
        body = body[:i] + ADD.strip() + "\n\n" + body[i:]
        io.open(BLOCKERS, "w", encoding="utf-8").write(body)
        print("appended the two tool confirmations")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R691 addendum: find_xref_signatures and trace_data_flow also find no incoming edge\n\n"
         "Five independent probes now agree that the fake-data region and the locale key have no\n"
         "visible incoming references in this IDB."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True,
    )
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:200]))


if __name__ == "__main__":
    main()
