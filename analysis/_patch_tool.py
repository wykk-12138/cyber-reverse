import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()

old_run = '''def run_tests(test_filter):
    """Return (exit_code, tail) for a filtered test run. `exit_code` is None when the run was cut off."""
    try:
        result = subprocess.run(
            [DOTNET, "test", os.path.join(REPO, "tests", "Cybersole.Tests",
                                         "Cybersole.Tests.csproj"),
             "--filter", test_filter, "-v", "q", "--nologo"],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return None, ["timeout after %ds" % RUN_TIMEOUT_SECONDS]
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]
'''

new_run = '''def run_tests(test_filter, trx=None):
    """Return (exit_code, tail) for a filtered test run. `exit_code` is None when the run was cut off.

    R206: `trx` writes a result file, because `-v q` prints a count and not the names. Without it a red
    restore-verification says "1 failed" and nothing else, which is not enough to act on.
    """
    args = [DOTNET, "test", os.path.join(REPO, "tests", "Cybersole.Tests",
                                        "Cybersole.Tests.csproj"),
            "--filter", test_filter, "-v", "q", "--nologo"]
    if trx:
        args += ["--logger", "trx;LogFileName=" + trx]
    try:
        result = subprocess.run(
            args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return None, ["timeout after %ds" % RUN_TIMEOUT_SECONDS]
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]


def failed_names(trx):
    """The tests a trx marks Failed, so a red verdict can name them instead of counting them."""
    if not trx or not os.path.exists(trx):
        return []
    try:
        import xml.etree.ElementTree as ET
        m = {"http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
        root = ET.parse(trx).getroot()
        out = []
        for r in root.iter("{%s}UnitTestResult" % m[list(m)[0]].strip("{}")):
            if r.get("outcome") == "Failed":
                out.append(r.get("testName"))
        return out
    except Exception as exc:                      # a broken trx must not hide the verdict
        return ["<trx unreadable: %s>" % exc]
'''

old_restore = '''    # confirm the tree really is back to green
    code, tail = run_tests("Speed!=Slow")
    state = "UNKNOWN (cut off)" if code is None else ("GREEN" if code == 0 else "RED")
    print("\\nrestored tree: " + state)
    for line in tail:
        print("  " + line[:110])
'''

new_restore = '''    # confirm the tree really is back to green. A red verdict must NAME the test: `-v q` only counts.
    trx = os.path.join(os.path.dirname(REPO), "analysis", "_mutation-restore.trx")
    if os.path.exists(trx):
        os.remove(trx)
    code, tail = run_tests("Speed!=Slow", trx=trx)
    state = "UNKNOWN (cut off)" if code is None else ("GREEN" if code == 0 else "RED")
    print("\\nrestored tree: " + state)
    for line in tail:
        print("  " + line[:110])
    for name in failed_names(trx):
        print("  FAILED: " + name)
'''

assert old_run in t and old_restore in t
t = t.replace(old_run, new_run).replace(old_restore, new_restore)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('patched tool')
