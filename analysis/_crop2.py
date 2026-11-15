from PIL import Image
import glob, os
shots = sorted(glob.glob(r"D:\projects\cyber-reverse\analysis\shots\shot*.png"))
box = (607, 192, 1030, 696)
os.makedirs(r"D:\projects\cyber-reverse\analysis\splashcrop", exist_ok=True)
for f in shots[4:9]:
    name = os.path.basename(f).replace("shot", "splash")
    out = os.path.join(r"D:\projects\cyber-reverse\analysis\splashcrop", name)
    Image.open(f).crop(box).save(out)
    print("saved", name)
