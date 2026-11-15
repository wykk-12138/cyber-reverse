import io
t = io.open(r"D:\projects\cyber-reverse\docs\GOAL.md", encoding="utf-8").read()
s = t.index("```\n把 Cybersole.exe"); e = t.index("```", s+5)
print("goal 块字符数:", e - s - 4)
