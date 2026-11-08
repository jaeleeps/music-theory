"""Make photo-like versions of the clean score images.

    python degrade.py images/clean images/photo           # "photo": small, tilted, blurred (the first test)
    python degrade.py images/clean images/phone phone     # "phone": a phone shot of the page on a table

"phone" follows music-web's phone variant: the page is bent (a slight wave), lies
on a dark textured table, is seen at a slant, has a light gradient and a soft
corner shadow, camera blur and noise, JPEG 85. The noise is seeded, so every
run makes the same images.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "photo"


def photo(im):
    w, h = im.size
    im = im.resize((int(w * 0.55), int(h * 0.55)), Image.LANCZOS)        # phone-photo resolution
    im = im.rotate(1.2, resample=Image.BICUBIC, expand=True, fillcolor=235)  # slight tilt
    im = im.point(lambda v: int(40 + v * 0.78))                           # greyish paper, weaker contrast
    return im.filter(ImageFilter.GaussianBlur(0.7)), 55


def phone(im, rng):
    # The excerpt on a page with margins.
    w, h = im.size
    page = Image.new("L", (w + 160, h + 200), 250)
    page.paste(im, (80, 100))
    pw, ph = page.size
    # Bend: each column shifts up or down a little, as a page that does not lie flat.
    a = np.asarray(page, dtype=np.float32)
    shift = 6 * np.sin(np.linspace(0, 2.2 * np.pi, pw))
    rows = np.clip(np.arange(ph)[:, None] - shift[None, :], 0, ph - 1).astype(int)
    a = a[rows, np.arange(pw)[None, :]]
    page = Image.fromarray(a.astype(np.uint8))
    # The table: dark and textured, larger than the page.
    tw, th = int(pw * 1.25), int(ph * 1.5)
    table = rng.normal(70, 12, (th, tw)).astype(np.float32)
    table = np.asarray(Image.fromarray(np.clip(table, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), dtype=np.float32)
    # Seen at a slant: the far (top) edge is narrower, and the page sits off-centre.
    ox, oy = (tw - pw) // 2, (th - ph) // 2
    dst = [(ox + 0.07 * pw, oy + 0.02 * ph), (ox + 0.95 * pw, oy + 0.08 * ph),
           (ox + 1.02 * pw, oy + 0.98 * ph), (ox - 0.03 * pw, oy + 0.93 * ph)]
    # Pillow maps output pixels to input points, so solve table -> page.
    src_pts = [(0, 0), (pw, 0), (pw, ph), (0, ph)]
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src_pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    coeffs = np.linalg.solve(np.array(A), np.array(b))
    warped = page.transform((tw, th), Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC, fillcolor=0)
    mask = Image.new("L", page.size, 255).transform((tw, th), Image.PERSPECTIVE, tuple(coeffs), Image.BILINEAR, fillcolor=0)
    m = np.asarray(mask, dtype=np.float32) / 255
    img = np.asarray(warped, dtype=np.float32) * m + table * (1 - m)
    # Light: brighter at the top left, with a soft shadow in the bottom-right corner.
    yy, xx = np.mgrid[0:th, 0:tw]
    light = 1.05 - 0.45 * (xx / tw * 0.6 + yy / th * 0.4)
    light -= 0.45 * np.exp(-(((xx - tw) / (0.35 * tw)) ** 2 + ((yy - th) / (0.35 * th)) ** 2))
    img = img * light
    img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    # Phone resolution, camera blur, sensor noise.
    img = img.resize((int(tw * 0.55), int(th * 0.55)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.9))
    a = np.asarray(img, dtype=np.float32) + rng.normal(0, 8, (img.height, img.width))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), 85


for k in "ABCD":
    im = Image.open(f"{src}/score_{k}.png").convert("L")
    if mode == "phone":
        im, quality = phone(im, np.random.default_rng(1))
    else:
        im, quality = photo(im)
    im.save(f"{out}/{mode}_{k}.jpg", quality=quality)
    print(k, im.size)
