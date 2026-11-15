import io

p = r"D:\projects\cyber-reverse\replica\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()

# a cut-off run gets its own verdict instead of being classified as "caught"
old = '''            code, tail = run_tests(m["test"])
            verdict = classify(code, tail)'''
new = '''            code, tail = run_tests(m["test"])
            verdict = classify_hung()["verdict"] if code is None else classify(code, tail)'''
if old not in t:
    raise SystemExit("call anchor missing")
t = t.replace(old, new, 1)

# the final green check must also survive a cut-off
old2 = '''    code, tail = run_tests("Speed!=Slow")
    print("\\nrestored tree: " + ("GREEN" if code == 0 else "RED"))'''
new2 = '''    code, tail = run_tests("Speed!=Slow")
    state = "UNKNOWN (cut off)" if code is None else ("GREEN" if code == 0 else "RED")
    print("\\nrestored tree: " + state)'''
if old2 not in t:
    raise SystemExit("green anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("a cut-off run is its own verdict")
