import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\verify_last.txt"
t = io.open(p, encoding="utf-8", errors="replace").read()

i = t.find("TheFlowProducesARealToken")
print("index:", i)
if i > 0:
    seg = t[max(0, i - 300): i + 1500]
    io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\kasada_fail.txt", "w",
            encoding="utf-8", newline="").write(seg)
    print("written", len(seg))
else:
    # find the slow-tests block instead
    j = t.find("slow tests")
    io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\kasada_fail.txt", "w",
            encoding="utf-8", newline="").write(t[max(0, j - 200): j + 2000])
    print("slow block written")
