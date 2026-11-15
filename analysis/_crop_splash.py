from PIL import Image
import glob, os, re
shots = sorted(glob.glob(r"D:\projects\cyber-reverse\analysis\shots\shot*.png"))
print("frames:", len(shots))
im = Image.open(shots[0])
print("frame size:", im.size)
# screen is 2560 wide (rects are in that space); the capture is scaled
scale = im.size[0] / 2560.0
print("scale:", scale)
# splash rect from the log
L, T, W, H = 759, 241, 529, 630
box = (int(L*scale), int(T*scale), int((L+W)*scale), int((T+H)*scale))
print("crop box:", box)
for f in shots[4:9]:
    out = f.replace("shot", "splash")
    Image.open(f).crop(box).save(out)
    print("saved", os.path.basename(out))
