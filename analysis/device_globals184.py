import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

# DEVICE_GLOBALS is a Set([...]) — find it and the code that uses it
i = text.find("const DEVICE_GLOBALS = new Set([")
if i < 0:
    raise SystemExit("DEVICE_GLOBALS not found")

# find the end of the Set(...) call
j = text.index("]);", i) + 3
segment = text[i:j]
names = re.findall(r'"((?:[^"\\]|\\.)*)"', segment)
print("DEVICE_GLOBALS:", len(names))

# the code around its use
print(text[max(0, i - 1500):i + 200])
print("========= after =========")
print(text[j:j + 2600])
