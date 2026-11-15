import io

p = r"D:\projects\cyber-reverse\replica\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()

old = '''def run_tests(test_filter):
    """Return (exit_code, tail) for a filtered test run."""
    result = subprocess.run(
        [DOTNET, "test", os.path.join(REPO, "tests", "Cybersole.Tests",
                                     "Cybersole.Tests.csproj"),
         "--filter", test_filter, "-v", "q", "--nologo"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]'''

new = '''#: A mutated build can make a browser-backed test loop forever, and an unbounded run then says nothing at all —
#: it neither fails nor finishes. Rounds 180-181 hit exactly that: every mutation looked identical to a hang. So each
#: run is bounded, and a bound is reported as its own verdict ("hung") rather than folded into "caught".
RUN_TIMEOUT_SECONDS = 600


def run_tests(test_filter):
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
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]'''

if old not in t:
    raise SystemExit("run_tests anchor missing")
t = t.replace(old, new, 1)

# classify: a cut-off run is reported separately
old2 = '''def classify(code, tail):'''
new2 = '''def classify_hung():
    """Say what a cut-off run means: the mutation did not just fail a guard, it stopped the guard finishing."""
    return {"verdict": "hung", "why": "the run did not finish inside %ds" % RUN_TIMEOUT_SECONDS}


def classify(code, tail):'''
if old2 not in t:
    raise SystemExit("classify anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("run_tests is bounded")
