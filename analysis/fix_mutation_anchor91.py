import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()

# R91 added a module: the anchor moved from 61 to 62 and the decoy from 60 to 61.
old_find = '"find": "**61 个注册模块",'
new_find = '"find": "**62 个注册模块",'
old_replace = '"replace": "**60 个注册模块",'
new_replace = '"replace": "**61 个注册模块",'

if old_find not in t:
    raise SystemExit("find anchor missing")
t = t.replace(old_find, new_find, 1)

if old_replace not in t:
    raise SystemExit("replace anchor missing")
t = t.replace(old_replace, new_replace, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("round-164 anchors moved to 62/61")
