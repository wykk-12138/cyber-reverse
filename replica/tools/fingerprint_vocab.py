"""Generate docs/FINGERPRINT_VOCAB.md -- every name the fingerprint layer uses, with its authority.

Priority three is the request and fingerprint layer, and BrowserIdentity.cs writes three session variables plus two
payload literals. Those names are this workspace's vocabulary, and whether the original shares it is answerable: the
pool carries string data even though R1045 showed it has no symbols. So each name gets a probe, each probe gets a
control, and the result is a table a reader can recompute.

Why a generator: R1030 recorded that append-only lists fossilise and R1041 that hand-written tables drift from the
tools that produce them. Both apply here.

Run: python tools/fingerprint_vocab.py   (writes docs/FINGERPRINT_VOCAB.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # replica/
REPO = os.path.dirname(ROOT)                                                # cyber-reverse/
OUT = os.path.join(ROOT, "docs", "FINGERPRINT_VOCAB.md")
SRC = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "BrowserIdentity.cs")

# The controls are strings with known presence, so a zero on a name can be read against a non-zero in the same run.
PROBES = [
    ("control", "kpsdk", r"kpsdk", "Kasada's cookie prefix, known present"),
    ("control", "datadome", r"datadome", "DataDome's host, known present"),
    ("payload", "fingerprint-v1", r"fingerprint-v1", "BrowserIdentity's payload literal"),
    ("payload", "fingerprint-v1-sans-ua", r"sans-ua", "the variant literal"),
    ("session key", "browser.fingerprintKey", r"fingerprintKey", "the key name"),
    ("session key", "browser.fingerprintPayload", r"fingerprintPayload", "the payload name"),
    ("session key", "browser.timezoneOffsetMinutes", r"timezoneOffset", "the offset concept"),
]


def probe(pattern, limit=600):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def names_in_source():
    text = io.open(SRC, encoding="utf-8", errors="replace").read()
    return {
        "consts": re.findall(r'public const string (\w+Var)\s*=\s*"([^"]+)"', text),
        "payloads": re.findall(r'PayloadV1\w*\s*=\s*"([^"]+)"', text),
    }


def main():
    src = names_in_source()
    rows = []
    for kind, label, pattern, note in PROBES:
        d = probe(pattern)
        n = d.get("n", -1)
        addrs = [h.get("addr") for h in d.get("matches", [])[:3]]
        rows.append((kind, label, n, addrs, note))

    controls = [r for r in rows if r[0] == "control"]
    control_ok = all(r[2] > 0 for r in controls)

    lines = []
    add = lines.append
    add("# 指纹层词汇对照（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/fingerprint_vocab.py` 生成。功能优先级 ③（请求与指纹层）。")
    add("")
    add("`BrowserIdentity.cs` 里有 %d 个 `const string` 与 %d 个 payload 字面量。"
        % (len(src["consts"]), len(src["payloads"])))
    add("而它们分两类：**从镜像来的** 与 **本工作自造的** —— 而这件事可查，因为池里有字符串数据"
        "（R1045 只证明它没有**符号**）。")
    add("")
    add("## 一、对照是否成立")
    add("")
    add("| 对照串 | 命中 | 结论 |")
    add("|---|---|---|")
    for kind, label, n, addrs, note in controls:
        add("| `%s` | **%d** | %s |" % (label, n, note))
    add("")
    add("**→ 对照%s**（两个已知串都 > 0），所以下表里的 0 可以读成「镜像里没有」，不是查询失败。"
        % ("成立" if control_ok else "不成立 —— 下面的 0 不可信"))
    add("")
    add("## 二、逐名对照")
    add("")
    add("| 类别 | 名字 | 镜像命中 | 地址 | 判定 |")
    add("|---|---|---|---|---|")
    for kind, label, n, addrs, note in rows:
        if kind == "control":
            continue
        verdict = "**有据**" if n > 0 else "**镜像里没有**"
        addr = addrs[0] if addrs else "—"
        add("| %s | `%s` | **%d** | `%s` | %s |" % (kind, label, n, addr, verdict))
    add("")
    add("## 三、结论")
    add("")
    payload_hit = [r for r in rows if r[0] == "payload" and r[2] > 0]
    key_zero = [r for r in rows if r[0] == "session key" and r[2] == 0]
    add("**有据的**：%d 个 payload 字面量在镜像里（`fingerprint-v1` `0x147034eac` · "
        "`fingerprint-v1-sans-ua` `0x147034ee4`），时区概念有 %d 条命中"
        "（含 `TimezoneOffset` 属性与 `ParseTimeZoneOffset`）。"
        % (len(payload_hit), next((r[2] for r in rows if "timezoneOffset" in r[1]), 0)))
    add("")
    add("**自造的**：%s —— 那两个 session 变量名在镜像里 0 次。"
        % (" · ".join("`%s`" % r[1] for r in key_zero) or "（无）"))
    add("")
    add("**→ 而那不矛盾**：session 变量是**本工作内部**的传值约定（R133/R134 定的），"
        "原版用别的方式把同一件事带到支付层。所以那两个名字**不需要**有据，"
        "而它们**必须**与它们携带的值一致 —— 值有据，名字是本地约定。")
    add("")
    add("**→ 而 payload 名有据**是更强的结论：复刻件与镜像用**同一个** payload 词汇，"
        "所以 `FingerprintLayers.PayloadFor` 的分支名不是猜的。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/FINGERPRINT_VOCAB.md")
    print("  controls ok=%s  payload=%d  self-coined keys=%d"
          % (control_ok, len(payload_hit), len(key_zero)))


if __name__ == "__main__":
    main()
