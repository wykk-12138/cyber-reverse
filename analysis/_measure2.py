from PIL import Image
def runs_of(path, y0, y1, thresh=90, scale_hint=None):
    im = Image.open(path).convert("RGB"); px = im.load(); W, H = im.size
    cols = []
    for x in range(W):
        ink = 0
        for y in range(y0, y1):
            r, g, b = px[x, y]
            if r > thresh and g > thresh and b > 100: ink += 1
        cols.append(ink)
    out, cur = [], None
    for x, v in enumerate(cols):
        if v > 0: cur = [x, x] if cur is None else [cur[0], x]
        else:
            if cur and cur[1]-cur[0] >= 2: out.append(tuple(cur))
            cur = None
    if cur: out.append(tuple(cur))
    return W, H, out

# find the header band automatically: scan for a band with ~5 separated runs near the top third
p2 = r"C:\Users\wykk\.dsh\attachments\v1\objects\74\74bc8f53fda0ef97ed0809aa5e802a3551e8ccf0eb0777548a1db400d0b06506"
for band in ((180, 205), (185, 210), (175, 200)):
    W, H, r = runs_of(p2, *band)
    print("band", band, "size", W, H, "runs:", r[:6], "...", r[-2:])
