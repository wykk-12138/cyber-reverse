from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\1d\1d2648ed1ffb14ff8f33dfa4d94c5079c4664c46de7e66288481b9a334dba1aa"
im = Image.open(p).convert("RGB")
px = im.load()
W, H = im.size
# the footer button row sits at y ~ 920-955; find the right-most ink of the header band too
def ink_runs(y0, y1, thresh=90):
    runs, cur = [], None
    for x in range(W):
        ink = any(all(c > thresh for c in px[x, y][:3]) for y in range(y0, y1))
        if ink:
            cur = [x, x] if cur is None else [cur[0], x]
        else:
            if cur and cur[1]-cur[0] >= 2: runs.append(tuple(cur))
            cur = None
    if cur: runs.append(tuple(cur))
    return runs
print("header band 150..195 last runs:", ink_runs(150, 195)[-4:])
print("title band  85..115 last runs:", ink_runs(85, 115)[-4:])
