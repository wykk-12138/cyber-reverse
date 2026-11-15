"""Generate docs/SHAPE_GAPS.md: every member-shape mismatch with a disposition (R575).

`tools/shape_audit.py` reports a count and a per-row kind (`?` / `method` / `prop-get`). A count is not a
disposition — 80 mismatches could be 80 to-dos or 80 structural differences, and the number cannot tell you which.
This is the same move `analysis/type_gaps_report.py` made for the 46 absent types: turn a count into per-row
statements, each of which a reader can argue with.

The classification below is mechanical and stated in the output:

    Window 子类的 Close            -> hard constraint: Window.Close() already exists
    replica=method                 -> the member exists as a method; the binding says Property. Converting it
                                      needs a *selection model* for the parameter, which the replica does not have
    replica=prop-get, computed     -> the property is an expression body over other state; a setter would be wrong
    replica=prop-get, stored       -> a real field-backed property missing only the setter
    replica=? and found elsewhere  -> the name exists on another class (a rename to record)
    replica=? and not found        -> genuinely absent on that class

For the `?` rows the script also searches the whole source for the name, so "absent" and "renamed" stop being the
same word. That search is a **name** search; it does not establish that the found member means the same thing.

Every disposition is derived from source text; none of it is behavioural evidence.
"""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
REPLICA = os.path.join(ROOT, "replica")
SRC = os.path.join(REPLICA, "src")
OUT = os.path.join(ROOT, "docs", "SHAPE_GAPS.md")
PY = r"C:\Python312\python.exe"

ROW = re.compile(r"\s+(\S+)\s+(\S+)\s+evidence=(\S+)\s+replica=(\S+)")


def run_audit():
    res = subprocess.run([PY, "tools/shape_audit.py"], cwd=REPLICA,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    rows = []
    for line in res.stdout.splitlines():
        m = ROW.match(line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return rows, res.stdout


def load_sources():
    files = {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".cs"):
                path = os.path.join(dirpath, fn)
                try:
                    files[path] = io.open(path, encoding="utf-8", errors="replace").read()
                except OSError:
                    pass
    return files


def where_declared(files, cls, member):
    """All (file, class) places declaring `member` as a property or method, plus this class's own body."""
    pat = re.compile(r"(public|private|internal|protected)\s+[\w<>\[\],?\s\.]+\b" + re.escape(member) + r"\b\s*[\({=]")
    hits = []
    for path, text in files.items():
        if not pat.search(text):
            continue
        # crude owner: the nearest preceding `class X`
        for m in re.finditer(r"\bclass\s+(\w+)", text):
            body_start = text.find("{", m.end())
            if body_start < 0:
                continue
            depth, i = 0, body_start
            while i < len(text):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            body = text[body_start:i + 1]
            if pat.search(body):
                hits.append((os.path.basename(path), m.group(1)))
    return hits


def dispose(cls, member, evidence, kind, files):
    if member == "Close" and kind == "?":
        return ("**结构差异，不补**：`Window.Close()` 已经存在（继承而来）。原版把它当可绑定属性，"
                "复刻件的窗口用的是继承来的方法 —— 再加一个 `ICommand Close` 会遮蔽基类成员。")

    if kind == "method":
        return ("**需要选择模型**：成员在复刻件里是**带参数的方法**，而绑定证据说是 `Property`。"
                "把它改成 `ICommand` 需要一个「当前选中项」来喂参数，而复刻件的该类没有这个概念。"
                "在没有原版可观察之前，加一个选择模型就是发明。")

    if kind == "prop-get":
        return "**读**：见下方逐条（计算属性 vs 存储属性）"

    if kind == "?":
        hits = where_declared(files, cls, member)
        others = [(f, c) for f, c in hits if c != cls]
        if not hits:
            return "**真缺**：全源码里没有 `%s` 这个名字。补它需要先知道它绑到什么。" % member
        if not others:
            return "**同名但形状不同**：本类里能搜到 `%s`，但 `shape_audit` 判为不存在（可能是常量或不同修饰符）。" % member

        # A common name found on an unrelated class proves nothing. `BLOCKERS.md` §5 documented this exact trap
        # for the "best owning class" heuristic: `Helpers.ObservableDictionary`2 -> AccountGrid` matched only
        # because both have a member called `Count`. Filing such a hit as a rename would be the same mistake.
        distinctive = len(member) >= 10
        names = "、".join("`%s.%s`" % (c, member) for f, c in others[:3])
        if distinctive:
            return ("**可能改名，判据弱**：`%s` 是个有识别度的名字，在 %s 上出现。"
                    "**同名仍不等于同成员**，要确认得读那处的实现。记录为弱证据，不作为结案。"
                    % (member, names))
        return ("**Unknown（同名撞名，判据无判别力）**：`%s` 是通用名，源码里有 %d 个类都叫它（如 %s）。"
                "「在别的类上找到同名成员」**不能**推断是同一个功能 —— 这正是 `BLOCKERS.md` §5 记下的那个陷阱。"
                "要结案只能读该类有没有这块功能，或等原版可观察。"
                % (member, len(others), names))

    return "**未分类**"


def main():
    rows, raw = run_audit()
    files = load_sources()

    lines = [
        "# 成员形状差异：%d 条逐条处置" % len(rows),
        "",
        "> 生成物：`python analysis/shape_gaps_report.py`。数据来自 `python tools/shape_audit.py` 的原始输出，",
        "> 加上对 `replica/src/**/*.cs` 的**名字**搜索。",
        "> 判据 a 要求把缺口结案（可做 / 结构差异 / 不可得）—— 这份文件就是那一步。",
        "",
        "## 怎么读",
        "",
        "- `evidence=` 是原版绑定描述符里记的访问器种类；`replica=` 是复刻件里同名成员的形状。",
        "- **处置是机械判据**，只看源码文本，不含任何行为证据。它能被读者反驳，这正是它的用处。",
        "",
        "## 汇总",
        "",
    ]

    groups = {}
    detail = []
    for cls, member, evidence, kind in rows:
        d = dispose(cls, member, evidence, kind, files)
        key = d.split("：")[0].strip("*")
        if kind == "prop-get":
            key = "prop-get（逐条看）"
        groups[key] = groups.get(key, 0) + 1
        detail.append((cls, member, evidence, kind, d))

    lines.append("| 处置 | 条数 |")
    lines.append("|---|---|")
    for k, v in sorted(groups.items(), key=lambda kv: -kv[1]):
        lines.append("| %s | %d |" % (k, v))
    lines += ["", "## 逐条", ""]

    for cls, member, evidence, kind, d in sorted(detail):
        lines.append("### `%s.%s`" % (cls, member))
        lines.append("")
        lines.append("- evidence: `%s`   replica: `%s`" % (evidence, kind))
        lines.append("- 处置：%s" % d)
        lines.append("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print("wrote SHAPE_GAPS.md  (%d rows)" % len(detail))
    for k, v in sorted(groups.items(), key=lambda kv: -kv[1]):
        print("  %-40s %d" % (k, v))


if __name__ == "__main__":
    main()
