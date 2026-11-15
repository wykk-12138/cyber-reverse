import io

p = r"D:\projects\cyber-reverse\analysis\parse_check108.ps1"
t = io.open(p, encoding="utf-8").read()

t = t.replace(r"$path = 'C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1'",
              r"$path = 'D:\projects\cyber-reverse\replica\tools\verify.ps1'", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("parser target is the D: path now")
