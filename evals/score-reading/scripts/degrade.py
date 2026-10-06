import sys
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
for k in "ABCD":
    im = Image.open(f"{src}/score_{k}.png").convert("L")
    w, h = im.size
    im = im.resize((int(w * 0.55), int(h * 0.55)), Image.LANCZOS)        # phone-photo resolution
    im = im.rotate(1.2, resample=Image.BICUBIC, expand=True, fillcolor=235)  # slight tilt
    im = im.point(lambda v: int(40 + v * 0.78))                           # greyish paper, weaker contrast
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    im.save(f"{out}/photo_{k}.jpg", quality=55)
    print(k, im.size)
