from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\1d\1d2648ed1ffb14ff8f33dfa4d94c5079c4664c46de7e66288481b9a334dba1aa"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
ym = 930
def lum(c): return (c[0]*299 + c[1]*587 + c[2]*114)//1000
row = [lum(px[x, ym]) for x in range(W)]
bg = min(row)  # the page background is the darkest value on this row
runs, cur = [], None
for x, v in enumerate(row):
    if v > bg + 4:
        cur = [x, x] if cur is None else [cur[0], x]
    else:
        if cur and cur[1] - cur[0] > 30: runs.append((cur[0], cur[1], cur[1] - cur[0] + 1))
        cur = None
if cur and cur[1] - cur[0] > 30: runs.append((cur[0], cur[1], cur[1] - cur[0] + 1))
print("bg lum", bg)
print("button runs on y=%d (x0, x1, width):" % ym)
for r in runs: print("   ", r)
# also the vertical extent of the first run
if runs:
    x0, x1, _ = runs[0]
    xm = (x0 + x1) // 2
    ys = [y for y in range(H - 160, H) if lum(px[xm, y]) > bg + 4]
    print("first button vertical extent:", ys[0], "..", ys[-1], "height", ys[-1] - ys[0] + 1)
