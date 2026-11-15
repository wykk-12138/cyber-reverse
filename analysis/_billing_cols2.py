from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\77\77cdbd55c5aea6f992b83a3a360423f98e76746c660650a8e09d011587dfc51a"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
print("billing at", W, H)
def clusters(y0, y1, gap=14, thresh=85):
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
print("1375 header:", clusters(200, 225))
