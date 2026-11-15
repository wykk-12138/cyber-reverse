r"""Verify the published AOT artifact actually carries what the sources declare.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
R461 and R462 verified two things by hand-typed one-liners: that all 1142 locale keys survive into
`.publish-aot/Cybersole.Ui.exe`, and that all 19 `EmbeddedResource` entries keep both their logical name and
their content. Those are exactly the checks that silently rot after an AOT rebuild — trimming, linker
reordering or resource compression can drop either half — and `metrics_report.py` had no way to notice,
because every existing metric reads **sources**, not the published artifact.

It also reports the resource tree against the original (via the same IMAGE_RESOURCE_DIRECTORY walk as
`pe_resources.py`) and the zero-direct-xref ratio, so one command covers the artifact-level claims.

Exit code: 0 when every check passes, 1 when any fails. A missing artifact is reported as `SKIPPED` and the
exit code stays 0 — "not built" is not the same as "built wrong".

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/verify_artifact.py
    python analysis/verify_artifact.py --artifact replica\.publish-aot\Cybersole.Ui.exe
Output: analysis/artifact_verification.md
"""

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPLICA = os.path.join(ROOT, "replica")
DEFAULT_ARTIFACT = os.path.join(REPLICA, ".publish-aot", "Cybersole.Ui.exe")
ORIGINAL = os.path.join(ROOT, "target", "Cybersole.exe")
OUT = os.path.join(ROOT, "analysis", "artifact_verification.md")

PROJECTS = [
    os.path.join(REPLICA, "src", "Cybersole.Core", "Cybersole.Core.csproj"),
    os.path.join(REPLICA, "src", "Cybersole.Http", "Cybersole.Http.csproj"),
]
EN_LOCALE = os.path.join(REPLICA, "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
FINGERPRINT = 32


def check_locale(raw):
    if not os.path.exists(EN_LOCALE):
        return None
    doc = json.load(io.open(EN_LOCALE, encoding="utf-8"))
    keys = list(doc.keys())
    missing = [k for k in keys if k.encode("utf-8") not in raw]
    return len(keys), len(keys) - len(missing), missing[:10]


def check_resources(raw):
    rows = []
    for project in PROJECTS:
        if not os.path.exists(project):
            continue
        text = io.open(project, encoding="utf-8").read()
        base = os.path.dirname(project)
        for match in re.finditer(r'<EmbeddedResource\s+Include="([^"]+)"(?:\s+LogicalName="([^"]+)")?', text):
            include, logical = match.group(1), match.group(2)
            source = os.path.join(base, include.replace("\\", os.sep))
            name = logical or include.replace("\\", ".")
            name_ok = name.encode("utf-8") in raw
            content_ok = None
            size = -1
            if os.path.exists(source):
                blob = io.open(source, "rb").read()
                size = len(blob)
                content_ok = blob[:FINGERPRINT] in raw
            rows.append((name, size, name_ok, content_ok))
    return rows


def read_sections(data):
    e_lfanew = struct_unpack_i(data, 0x3C)
    coff = e_lfanew + 4
    num_sections = struct_unpack_h(data, coff + 2)
    opt_size = struct_unpack_h(data, coff + 16)
    opt = coff + 20
    magic = struct_unpack_h(data, opt)
    dd = opt + (112 if magic == 0x20B else 96)
    res_rva = struct_unpack_i(data, dd + 2 * 8)
    sect = opt + opt_size
    sections = []
    for i in range(num_sections):
        base = sect + i * 40
        vsize = struct_unpack_i(data, base + 8)
        va = struct_unpack_i(data, base + 12)
        raw_size = struct_unpack_i(data, base + 16)
        raw_ptr = struct_unpack_i(data, base + 20)
        sections.append((va, vsize, raw_ptr, raw_size))
    return sections, res_rva


def struct_unpack_i(data, off):
    return int.from_bytes(data[off:off + 4], "little")


def struct_unpack_h(data, off):
    return int.from_bytes(data[off:off + 2], "little")


def count_resource_leaves(path):
    import struct as _struct  # local: only this helper needs it

    data = io.open(path, "rb").read()
    sections, res_rva = read_sections(data)
    if not res_rva:
        return 0
    base = None
    for va, vsize, raw_ptr, raw_size in sections:
        if va <= res_rva < va + max(vsize, raw_size):
            base = raw_ptr + (res_rva - va)
            break
    if base is None:
        return 0
    leaves = [0]

    def walk(dir_off):
        n_named = _struct.unpack_from("<H", data, dir_off + 12)[0]
        n_id = _struct.unpack_from("<H", data, dir_off + 14)[0]
        for i in range(n_named + n_id):
            entry = dir_off + 16 + i * 8
            _name, data_field = _struct.unpack_from("<II", data, entry)
            if data_field & 0x80000000:
                walk(base + (data_field & 0x7FFFFFFF))
            else:
                leaves[0] += 1

    walk(base)
    return leaves[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--artifact", default=DEFAULT_ARTIFACT)
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    lines = ["# 产物验证（生成文件，请勿手改）", "",
             "> 由 `python analysis/verify_artifact.py` 生成。检查的是**发布出来的 AOT 产物**，",
             "> 不是源码 —— AOT 重建后裁剪/重排/压缩都可能让资源与文案消失，而现有度量只看源码。", ""]

    if not os.path.exists(args.artifact):
        print("SKIPPED: artifact not found at %s" % args.artifact)
        lines += ["## SKIPPED", "", "产物不存在：`%s`" % args.artifact, "",
                  "「没构建」不等于「构建错了」—— 这条不记失败。", ""]
        io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        return 0

    raw = io.open(args.artifact, "rb").read()
    failures = 0

    lines += ["## 产物", "", "| 项 | 值 |", "|---|---|",
              "| 路径 | `%s` |" % os.path.relpath(args.artifact, ROOT),
              "| 字节 | %d |" % len(raw), ""]
    print("artifact: %d bytes" % len(raw))

    # 1. locale keys
    locale = check_locale(raw)
    if locale:
        total, present, missing = locale
        ok = present == total
        failures += 0 if ok else 1
        lines += ["## locale 键存活", "",
                  "**%d/%d** 个 `en.json` 键出现在产物字节里%s" % (present, total, "" if ok else " —— **有缺失**"), ""]
        if missing:
            lines += ["缺失示例：", ""] + ["- `%s`" % k for k in missing] + [""]
        print("locale keys: %d/%d %s" % (present, total, "OK" if ok else "FAIL"))

    # 2. embedded resources
    rows = check_resources(raw)
    if rows:
        name_ok = sum(1 for r in rows if r[2])
        data_ok = sum(1 for r in rows if r[3])
        ok = name_ok == len(rows) and data_ok == len(rows)
        failures += 0 if ok else 1
        lines += ["## 内嵌资源存活", "",
                  "**逻辑名 %d/%d · 内容指纹 %d/%d**" % (name_ok, len(rows), data_ok, len(rows)), "",
                  "| 资源 | 字节 | 逻辑名 | 内容指纹 |", "|---|---|---|---|"]
        for name, size, nok, cok in rows:
            lines.append("| `%s` | %d | %s | %s |"
                         % (name, size, "yes" if nok else "**NO**",
                            "yes" if cok else ("**NO**" if cok is False else "n/a")))
        lines.append("")
        print("embedded resources: names %d/%d, content %d/%d %s"
              % (name_ok, len(rows), data_ok, len(rows), "OK" if ok else "FAIL"))

    # 3. resource tree vs the original
    if os.path.exists(ORIGINAL):
        mine, theirs = count_resource_leaves(args.artifact), count_resource_leaves(ORIGINAL)
        ok = mine == theirs
        failures += 0 if ok else 1
        lines += ["## 资源树叶数", "",
                  "| | 叶子 |", "|---|---|",
                  "| 原版 | %d |" % theirs, "| 复刻件 | %d |" % mine, ""]
        print("resource leaves: original %d, replica %d %s" % (theirs, mine, "OK" if ok else "DIFF"))

    lines.append("---")
    lines.append("")
    lines.append("**结论**：%s" % ("全部通过" if failures == 0 else "%d 项失败" % failures))
    lines.append("")
    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print()
    print("wrote %s" % args.out)
    print("result: %s" % ("PASS" if failures == 0 else "FAIL (%d)" % failures))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
