from PIL import Image
import sys
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\1d\1d2648ed1ffb14ff8f33dfa4d94c5079c4664c46de7e66288481b9a334dba1aa"
im = Image.open(p).convert("RGB")
W, H = im.size
print("image", W, H)
# header band of the tasks table: find the row that contains the header text (y ~ 160-185 in a 980-tall shot)
band_top, band_bot = 150, 195
px = im.load()
cols = []
for x in range(W):
    ink = 0
    for y in range(band_top, band_bot):
        r, g, b = px[x, y]
        if r > 90 and g > 90 and b > 100:
            ink += 1
    cols.append(ink)
# group contiguous ink columns into runs
runs, cur = [], None
for x, v in enumerate(cols):
    if v > 0:
        if cur is None: cur = [x, x]
        else: cur[1] = x
    else:
        if cur is not None:
            if cur[1] - cur[0] >= 2: runs.append(tuple(cur))
            cur = None
if cur: runs.append(tuple(cur))
print("ink runs (x0,x1,width):")
for a, b in runs:
    print("  %4d .. %4d   w=%3d" % (a, b, b - a + 1))
