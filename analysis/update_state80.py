import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

old = "**847 通过 / 0 失败 / 2 跳过**"
new = "**852 通过 / 0 失败 / 2 跳过**"
if old in t:
    t = t.replace(old, new, 1)
    print("test count updated")
else:
    print("test count anchor missing")

anchor = "- **「不在屏幕上」≠「不在逻辑树里」。**"
add = '''- **同一个 Settings 页面对了之后，隔壁那页通常是同一份模板换一列。** R79 把 Custom Stores
  改成「表 + 弹窗」，R80 发现 Custom Sizes 是同一个形状（单列 + `Add Size(s)` 带括号），
  先找模板再补差异，比从零开始便宜得多。
- **「不知道」的代价有时只是多点一下。** R79 留着 Custom Sizes 不动的原因是「没点过那个弹窗」；
  R80 点开了，四个字串一目了然。**能点就点，别把它留成悬念。**
'''
if anchor in t and "同一个 Settings 页面对了之后" not in t:
    t = t.replace(anchor, add + anchor, 1)
    print("traps added")
else:
    print("trap anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
