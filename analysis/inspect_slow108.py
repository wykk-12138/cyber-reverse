import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

i = t.find("if ($slowExit -ne 0)")
out = t[max(0, i - 500): i + 800]
io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\slow_block.txt", "w",
        encoding="utf-8", newline="").write(out)
print("written", len(out))
print("set retry present:", "[retry] slow tests failed once" in t)
print("leftover flaked:", "$flaked" in t)
print("detail:", "green on retry (first pass lost a live host)" in t)
