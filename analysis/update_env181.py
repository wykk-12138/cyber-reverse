import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

old = "  这不是代码缺陷，但会让「八步全绿」的判定不可信，所以写进状态。\n"
new = ("  这不是代码缺陷，但会让「八步全绿」的判定不可信，所以写进状态。\n"
       "  **R181 追加**：清理后单块可跑（`test-chunks.ps1` 26/26 全绿），但**同一进程内连跑多个浏览器类**仍会卡死；\n"
       "  第 3 步（slow network）与第 7 步（mutation guards）在本机当晚已跑不完 —— 下一轮先重启机器再谈「全绿」。\n")

if old not in t:
    raise SystemExit("env anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("environment note extended")
