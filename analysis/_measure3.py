from PIL import Image
def clusters(path, y0, y1, gap=20, thresh=90):
    im = Image.open(path).convert("RGB"); px = im.load(); W, H = im.size
    ink = [any(all(c > thresh for c in px[x, y][:3]) or (px[x,y][0]>thresh and px[x,y][2]>100 and px[x,y][1]>thresh) for y in range(y0, y1)) for x in range(W)]
    boxes, cur = [], None
    last = -999
    for x, v in enumerate(ink):
        if v:
            if cur is None or x - last > gap:
                if cur: boxes.append(tuple(cur))
                cur = [x, x]
            else:
                cur[1] = x
            last = x
    if cur: boxes.append(tuple(cur))
    return W, H, boxes

a = r"C:\Users\wykk\.dsh\attachments\v1\objects\1d\1d2648ed1ffb14ff8f33dfa4d94c5079c4664c46de7e66288481b9a334dba1aa"
b = r"C:\Users\wykk\.dsh\attachments\v1\objects\74\74bc8f53fda0ef97ed0809aa5e802a3551e8ccf0eb0777548a1db400d0b06506"
for label, path, band in (("W1", a, (150, 195)), ("W2", b, (180, 210))):
    W, H, boxes = clusters(path, *band)
    print(label, "size", W, H, "clusters:", [(x0, x1) for x0, x1 in boxes])
