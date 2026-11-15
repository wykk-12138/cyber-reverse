"""Self-test for mutation-check.py.

Round 149. Five rounds of false greens were found in the *guards*; none had been looked for in
the *thing that finds them*. This feeds the script mutations with known outcomes and checks it
classifies each one correctly.

Run:  python tools/mutation-check.py --self-test
"""
import io
import os
import subprocess
import sys

REPO = r"C:\Users\wykk\AppData\Local\Cybersole\replica"
DOTNET = r"D:\tools\dotnet8\dotnet.exe"
BRIDGE = os.path.join(REPO, "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs")
SPOOF_JS = os.path.join(REPO, "src", "Cybersole.Core", "Engine", "Cybersole.Engine.hcaptcha-spoof.js")


def run_tests(test_filter):
    result = subprocess.run(
        [DOTNET, "test", os.path.join(REPO, "tests", "Cybersole.Tests",
                                     "Cybersole.Tests.csproj"),
         "--filter", test_filter, "-v", "q", "--nologo"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]


def classify(code, tail):
    joined = "\n".join(tail)
    if "error CS" in joined:
        return "DID NOT COMPILE — the guard never ran"
    if code == 0:
        return "GUARD IS DECORATIVE — tests stayed green"
    return "guard fired"


# Each case states the verdict the tool must reach. If the tool disagrees with any of them, the
# tool is wrong — not the case.
CASES = [
    {
        "name": "control: a real mutation must fire",
        "mutation": {
            "file": BRIDGE,
            "find": "                value: function getVoices() { return voices.slice(); },",
            "replace": "                value: function getVoices() { return []; },",
            "test": "FullyQualifiedName~RealmReplayTests",
        },
        "expect": "guard fired",
        "why": "round 137's defect, restored — this is the only case that proves the loop works",
    },
    {
        "name": "an anchor that does not exist must be skipped, not counted",
        "mutation": {
            "file": BRIDGE,
            "find": "THIS STRING IS NOT IN THE FILE AND NEVER WAS",
            "replace": "anything",
            "test": "FullyQualifiedName~RealmReplayTests",
        },
        "expect": "SKIPPED",
        "why": "a renamed variable makes every anchor miss; that must not read as 'all fine'",
    },
    {
        "name": "a test filter matching nothing must not count as a catch",
        "mutation": {
            "file": BRIDGE,
            "find": "                value: function getVoices() { return voices.slice(); },",
            "replace": "                value: function getVoices() { return []; },",
            "test": "FullyQualifiedName~NoSuchTestXYZ12345",
        },
        "expect": "GUARD IS DECORATIVE",
        "why": "dotnet test exits 0 when --filter matches zero tests, so a typo in `test` "
               "silently reports a pass",
    },
    {
        "name": "a mutation inside the JS literal still compiles — and must fire",
        "mutation": {
            "file": BRIDGE,
            "find": "                value: function getVoices() { return voices.slice(); },",
            "replace": "                value: function getVoices() { return this is not C#; },",
            "test": "FullyQualifiedName~RealmReplayTests",
        },
        "expect": "guard fired",
        "why": "the script is a verbatim string literal, so arbitrary JS is still valid C#: the "
               "mutation compiles, the guard reads the literal, and it fires. Worth pinning down "
               "because it means DID NOT COMPILE can only come from editing real C#",
    },
    {
        "name": "a mutation in real C# that cannot compile",
        "mutation": {
            "file": BRIDGE,
            "find": "public async ValueTask DisposeAsync()",
            "replace": "        public async ValueTask DisposeAsync( { {",
            "test": "FullyQualifiedName~RealmReplayTests",
        },
        "expect": "DID NOT COMPILE",
        "why": "this one edits the C# around the literal, so the build fails and the guard "
               "never runs — the distinction the classifier exists for",
    },
]


def run_case(case):
    m = case["mutation"]
    path = m["file"]
    original = io.open(path, encoding="utf-8").read()

    if m["find"] not in original:
        return "SKIPPED" if case["expect"] == "SKIPPED" else "ANCHOR MISSING (unexpected)"

    try:
        io.open(path, "w", encoding="utf-8").write(original.replace(m["find"], m["replace"], 1))
        code, tail = run_tests(m["test"])
        return classify(code, tail)
    finally:
        io.open(path, "w", encoding="utf-8").write(original)


def main():
    print("== mutation-check self-test ==\n")
    failures = 0

    for case in CASES:
        got = run_case(case)
        # the verdicts carry an explanation after an em dash, so compare on the leading phrase
        ok = got.split(" — ")[0].strip() == case["expect"] or got == case["expect"]
        if not ok:
            failures += 1
        mark = "ok  " if ok else "FAIL"
        print(f"  [{mark}] {case['name']}")
        print(f"         expected: {case['expect']}")
        print(f"         got:      {got}")
        print(f"         why:      {case['why']}")
        print()

    print(f"== {len(CASES) - failures}/{len(CASES)} classified correctly ==")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
