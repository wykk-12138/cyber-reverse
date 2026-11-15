from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\ef\efeb9fa4f7d398a8b0538dd16151241618401596cf2b8089e4664bcb52d83c12"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
print("billing at", W, H)
def clusters(y0, y1, gap=20, thresh=85):
    ink = [any(px[x, y][0] > thresh and px[x, y][1] > thresh and px[x, y][2] > 100 for y in range(y0, y1)) for x in range(W)]
    boxes, cur, last = [], None, -999
    for x, v in enumerate(ink):
        if v:
            if cur is None or x - last > gap:
                if cur: boxes.append(tuple(cur))
                cur = [x, x]
            else:
                cur[1] = x
            last = x
    if cur: boxes.append(tuple(cur))
    return boxes
# header band of the billing table (Profile / Email / Card Holder / Card / Shipping)
for band in ((180, 200), (185, 205), (175, 195)):
    print(band, clusters(*band))
