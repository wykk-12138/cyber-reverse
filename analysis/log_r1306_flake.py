"""R1306: record the one intermittent suite failure this round actually saw.

The first mutation pass ended with `tree: RED` on a single test —
KasadaPresetEchoTests.ATokenThatWasInjectedIsNotReportedAsComputed — with the message
`script threw: Object reference not set to …` where the test expects `injected`. It passes 3 of 3
standalone and the immediate re-run of the whole pass was green, so it is intermittent, not a
regression from this round's change (which touches Unzer only).

Writing it down matters more than the label: a flake that is quietly retried away becomes a suite whose
green means "green most of the time", and criterion (e) is quoted from that suite. The entry names the
exact assertion, the exact message, and what is *not* yet known — which is where the null comes from
inside the Jint-hosted sensor script.

Byte-level, UTF-8, appended to the blockers file.
"""
import io

PATH = 'docs/BLOCKERS.md'

BLOCK = """
---

## R1306 · 已知间歇失败（不是回归，但也不许当成通过）

- **用例**：`Cybersole.Tests.KasadaPresetEchoTests.ATokenThatWasInjectedIsNotReportedAsComputed`
- **实测**：同一轮变异里出现过 1 次；`--filter FullyQualifiedName~KasadaPresetEchoTests` 单独跑 **3/3 通过**；
  紧接着整轮重跑 **2579 通过 / 0 失败 / 2 跳过**、`tree: GREEN`。
- **失败原文**（取自 `analysis/_mutation-restore.trx`）：
  `Assert.Contains() Failure: Sub-string not found / String: "script threw: Object reference not set to" / Not found: "injected"`
- **判读**：`KasadaSolver.Solve` 在 `Runtime.TryExecute` 失败时把 Jint 的异常原样拼进 `Error`
  （`src/Cybersole.Stores/Scripts/KasadaSolver.cs:502`）。所以这是**传感器脚本在 Jint 宿主里抛了 NRE**，
  不是断言写错，也不是本轮改动（本轮只碰 Unzer）。
- **Unknown**：那个 null 是 `BrowserShim` 的哪个成员、在什么调用序下返回的。要定因得在 `KasadaSolver`
  里把 NRE 换成"哪个成员为空"的错误——那是独立一项工作，未做。
- **纪律**：这一轮不据此声称 criterion (e)「稳定通过」；METRICS 记录的是**本次运行的**结果，
  本次是绿的，而间歇性写在这里。
"""

text = io.open(PATH, encoding='utf-8').read()
if 'R1306' in text and 'ATokenThatWasInjectedIsNotReportedAsComputed' in text:
    print('already recorded, skipped')
else:
    with io.open(PATH, 'a', encoding='utf-8', newline='') as fh:
        fh.write(BLOCK)
    print('appended %d chars to %s' % (len(BLOCK), PATH))
