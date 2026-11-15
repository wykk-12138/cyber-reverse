from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\f9\f92901e4539cb15736c4d316424dcd3fb1ead7c7b51b0a039688cace53288f88"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
print("window image", W, H)
# The rail's group row (Group 1) is a lighter card; find its right edge along the row's centre line.
# row centre ~ y = 235
y = 235
row = [px[x, y] for x in range(W)]
# the card is lighter than the page background; find runs of the lighter tone
def lum(c): return (c[0]*299 + c[1]*587 + c[2]*114)//1000
vals = [lum(c) for c in row]
base = sorted(vals)[len(vals)//2]
print("median lum", base)
runs, cur = [], None
for x, v in enumerate(vals):
    if v > base + 3:
        cur = [x, x] if cur is None else [cur[0], x]
    else:
        if cur and cur[1]-cur[0] > 40: runs.append(tuple(cur))
        cur = None
if cur and cur[1]-cur[0] > 40: runs.append(tuple(cur))
print("lighter runs on y=%d:" % y, runs[:8])
