#!/usr/bin/env python3
"""Clean up a photo of a score and cut it into enlarged crops, so notes can be read up close.

Reading a whole page at once is unreliable; reading enlarged crops is not
(see references/score-input.md). Needs Pillow (preinstalled in most Python
sandboxes, including claude.ai's code execution). numpy is used when present.

    python3 zoom.py page.jpg --out crops/                       # horizontal strips (about one system each)
    python3 zoom.py page.jpg --out crops/ --strips 4 --cols 2   # 4 strips, each split in 2 halves
    python3 zoom.py page.jpg --out crops/ --box 0,0.5,0.5,1     # one region: left,top,right,bottom as fractions

Phone photos:

    python3 zoom.py page.jpg --out crops/ --flatten             # even out shadows and uneven light
    python3 zoom.py page.jpg --out crops/ --corners 0.08,0.05 0.95,0.07 0.97,0.96 0.04,0.93
                                                                # straighten the page inside these corners
                                                                # (top left, top right, bottom right, bottom left;
                                                                # fractions of the picture, or pixels)
    python3 zoom.py crops/page.png --out crops/ --box 0,0,0.5,0.5   # re-check a region of the cleaned page

--corners and --flatten save the cleaned page as page.png in the --out folder;
use it as the input for later --box crops instead of cleaning the photo again.

Every run prints the staff spacing it measured (the distance between two staff
lines). Crops are enlarged so that spacing is about 40 px, which is easy to
read; --scale sets the factor by hand. Without --strips and --cols, crops are
sized from that spacing too: about one piano system tall and a few bars wide,
over the inked part of the page. Each crop overlaps its neighbours slightly
and is sharpened. Then look at the crops one at a time.
"""
import argparse
import os
import sys
from collections import Counter

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    sys.exit("Pillow is not installed (pip install pillow). Without it, ask the student for a closer, "
             "higher-resolution photo of one system at a time instead.")

try:
    import numpy as np
except ImportError:
    np = None

# Staff spacing (pixels between two staff lines) that crops are enlarged to.
# Readers in testing chose about 40-80 px by hand on phone photos.
TARGET_SPACING = 40
# Below this, the source picture is too coarse: enlarging cannot add the missing detail.
# (Claude read zoomed crops at about 6.5 px spacing at 98-100%; see docs/score-reading-test.md.)
MIN_SPACING = 5
MAX_SCALE = 8.0


def staff_spacing(img):
    """The distance between two staff lines, in pixels, or None when no staff is found.

    Down a narrow vertical strip through a staff, darkness rises and falls once
    per staff line, so the strip's darkness profile correlates best with itself
    shifted by one staff spacing. Grey levels are used as they are (no
    threshold), which keeps faint, blurred lines in photos; narrow strips keep a
    slight tilt from smearing the lines together.
    """
    small = img
    if img.width > 1600:  # plenty for measuring; keeps the pure-Python loop quick
        small = img.resize((1600, max(1, round(img.height * 1600 / img.width))), Image.BILINEAR)
    factor = img.width / small.width
    strip = max(4, small.width // 100)
    votes = Counter()
    for x in range(small.width // 10, small.width - small.width // 10 - strip, strip):
        band = small.crop((x, 0, x + strip, small.height)).resize((1, small.height), Image.BOX)
        dark = [255 - v for v in band.tobytes()]
        # High-pass: subtract a running mean over about two staff heights, so page
        # edges, the table and light gradients do not swamp the lines.
        half, run = 40, [0]
        for v in dark:
            run.append(run[-1] + v)
        n = len(dark)
        prof = [dark[i] - (run[min(n, i + half)] - run[max(0, i - half)]) / (min(n, i + half) - max(0, i - half))
                for i in range(n)]
        energy = sum(v * v for v in prof)
        if energy == 0:
            continue
        corr = [sum(prof[i] * prof[i + lag] for i in range(n - lag)) / energy for lag in range(0, min(61, n // 3))]
        # The first clear peak after the curve has dropped: one staff spacing.
        for lag in range(4, len(corr) - 1):
            if corr[lag] >= corr[lag - 1] and corr[lag] > corr[lag + 1] and corr[lag] > 0.25:
                votes[lag] += 1
                break
    if sum(votes.values()) < 3:
        return None
    spacing = max(votes, key=lambda s: votes[s - 1] + 2 * votes[s] + votes[s + 1])
    return spacing * factor


def ink_box(img):
    """The rows and columns that hold ink, so crops skip blank margins (and a table's edge)."""
    small = img.resize((max(1, img.width // 4), max(1, img.height // 4)), Image.BOX)
    W, H = small.size
    data = small.tobytes()
    level = sum(data) / len(data) * 0.7
    rows = [sum(1 for v in data[y * W:(y + 1) * W] if v < level) for y in range(H)]
    cols = [sum(1 for y in range(H) if data[y * W + x] < level) for x in range(W)]
    # A row or column counts when it holds more ink than speckle would.
    ys = [y for y, n in enumerate(rows) if n > 0.02 * W]
    xs = [x for x, n in enumerate(cols) if n > 0.02 * H]
    if not ys or not xs:
        return 0, 0, img.width, img.height
    pad = 8
    return (max(0, 4 * xs[0] - pad), max(0, 4 * ys[0] - pad),
            min(img.width, 4 * xs[-1] + 4 + pad), min(img.height, 4 * ys[-1] + 4 + pad))


def parse_corners(values, W, H):
    """Four "x,y" pairs, as fractions (all within 0-1) or pixels."""
    if len(values) != 4:
        sys.exit("--corners needs four x,y points: top left, top right, bottom right, bottom left")
    try:
        pts = [tuple(float(v) for v in p.split(",")) for p in values]
    except ValueError:
        sys.exit(f"--corners points look like 0.1,0.05 (fractions) or 120,80 (pixels); got {values}")
    if any(len(p) != 2 for p in pts):
        sys.exit(f"--corners points look like 0.1,0.05 (fractions) or 120,80 (pixels); got {values}")
    if all(0 <= c <= 1 for p in pts for c in p):
        pts = [(x * W, y * H) for x, y in pts]
    return pts


def straighten(img, quad):
    """Warp the page inside quad (top left, top right, bottom right, bottom left) to an upright rectangle.

    Pillow's PERSPECTIVE transform wants, for each output pixel (u, v), the
    source point ((a u + b v + c) / (g u + h v + 1), (d u + e v + f) / (g u + h v + 1)):
    Heckbert's square-to-quad map, scaled to the output size.
    """
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = quad
    dist = lambda p, q: ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
    # Twice the page's size in the photo (up to about 16 MP): one resampling now
    # keeps detail that a second enlargement of a 1x page would blur.
    width, height = max(dist(quad[0], quad[1]), dist(quad[3], quad[2])), max(dist(quad[0], quad[3]), dist(quad[1], quad[2]))
    up = min(2.0, (16e6 / max(1.0, width * height)) ** 0.5)
    width, height = max(1, round(width * up)), max(1, round(height * up))
    sx, sy = x0 - x1 + x2 - x3, y0 - y1 + y2 - y3
    dx1, dx2, dy1, dy2 = x1 - x2, x3 - x2, y1 - y2, y3 - y2
    den = dx1 * dy2 - dx2 * dy1
    if abs(den) < 1e-9:
        sys.exit("--corners do not outline a page (are two of them the same point?)")
    g = (sx * dy2 - dx2 * sy) / den
    h = (dx1 * sy - sx * dy1) / den
    a, b = x1 - x0 + g * x1, x3 - x0 + h * x3
    d, e = y1 - y0 + g * y1, y3 - y0 + h * y3
    coeffs = (a / width, b / height, x0, d / width, e / height, y0, g / width, h / height)
    return img.transform((width, height), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=255)


def flatten(img):
    """Divide the picture by its own heavy blur: shadows and light gradients cancel, ink stays."""
    img = img.filter(ImageFilter.GaussianBlur(0.6))  # soften sensor noise (a median filter would erase thin staff lines)
    # The paper's brightness: a max filter drops the ink (otherwise dense passages
    # would count as shadow and wash out), then a blur smooths it. At quarter size, for speed.
    small = img.resize((max(1, img.width // 4), max(1, img.height // 4)), Image.BOX)
    small = small.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))
    light = small.resize(img.size, Image.BILINEAR)
    if np is not None:
        flat = np.asarray(img, dtype=np.float32) / (np.asarray(light, dtype=np.float32) + 1) * 255
        out = Image.fromarray(np.clip(flat, 0, 255).astype(np.uint8))
    else:
        from PIL import ImageMath
        ink, paper = img.convert("F"), light.convert("F")
        if hasattr(ImageMath, "lambda_eval"):  # Pillow 10.3+
            flat = ImageMath.lambda_eval(lambda e: e["a"] * 255 / (e["b"] + 1), a=ink, b=paper)
        else:
            flat = ImageMath.eval("a * 255 / (b + 1)", a=ink, b=paper)
        out = flat.convert("L")  # clamps to 0-255
    # Paper is now about 255 and thin lines only a little darker; a power curve
    # keeps the paper white and darkens everything else, so faint lines stay visible.
    return out.point([round(255 * (v / 255) ** 2.5) for v in range(256)])


def save(img, box, out, name, scale):
    crop = img.crop(box)
    crop = crop.resize((max(1, int(crop.width * scale)), max(1, int(crop.height * scale))), Image.LANCZOS)
    crop = ImageOps.autocontrast(crop, cutoff=1).filter(ImageFilter.UnsharpMask(radius=2, percent=120))
    path = os.path.join(out, name)
    crop.save(path)
    print(f"{path}  (from x {box[0]}-{box[2]}, y {box[1]}-{box[3]} of {img.width}x{img.height})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", required=True, help="folder for the crops (created if missing)")
    ap.add_argument("--strips", type=int, default=0, help="horizontal strips (default: about one piano system each)")
    ap.add_argument("--cols", type=int, default=0, help="split each strip into this many columns (default: a few bars each)")
    ap.add_argument("--box", help="single region as fractions: left,top,right,bottom")
    ap.add_argument("--scale", type=float, help="enlargement factor (default: from the staff spacing, else 3)")
    ap.add_argument("--corners", nargs=4, metavar="X,Y", help="page corners to straighten: TL TR BR BL")
    ap.add_argument("--flatten", action="store_true", help="even out shadows and uneven light (it also makes paper grain stronger)")
    args = ap.parse_args()

    try:
        img = ImageOps.exif_transpose(Image.open(args.image)).convert("L")
    except (FileNotFoundError, OSError) as e:
        sys.exit(f"Cannot open image: {e}")
    os.makedirs(args.out, exist_ok=True)

    # The cleaned page is saved too, so the corners and the lighting can be checked by eye.
    if args.corners:
        img = straighten(img, parse_corners(args.corners, *img.size))
    if args.flatten:
        img = flatten(img)
    if args.corners or args.flatten:
        page = os.path.join(args.out, "page.png")
        img.save(page)
        print(f"{page}  (cleaned page, {img.width}x{img.height})")

    W, H = img.size
    spacing = staff_spacing(img)
    scale = args.scale
    if spacing:
        print(f"staff spacing about {spacing:.0f} px")
        if spacing < MIN_SPACING:
            print(f"warning: staff spacing under {MIN_SPACING} px is too small to read reliably, even enlarged. "
                  "Ask for a closer photo of one system at a time.")
        if scale is None:
            scale = min(MAX_SCALE, max(1.5, TARGET_SPACING / spacing))
    else:
        print("staff spacing: not found (no clear staff lines; for a slanted photo, straighten it with --corners first)")
    if scale is None:
        scale = 3.0
    print(f"enlarging {scale:.1f}x")

    if args.box:
        try:
            l, t, r, b = (float(v) for v in args.box.split(","))
        except ValueError:
            sys.exit("--box needs four fractions: left,top,right,bottom")
        if not (0 <= l < r <= 1 and 0 <= t < b <= 1):
            sys.exit("--box needs 0 <= left < right <= 1 and 0 <= top < bottom <= 1")
        name = "box_" + "_".join(f"{v:g}" for v in (l, t, r, b)) + ".png"   # one file per region, so re-checks don't overwrite
        save(img, (int(l * W), int(t * H), int(r * W), int(b * H)), args.out, name, scale)
        return

    # Strips about one piano system tall (18 staff spacings) and a few bars (80) wide,
    # over the inked part of the page, overlapping so a system cut at one edge is whole in the next.
    left, top, right, bottom = ink_box(img)
    iw, ih = right - left, bottom - top
    strips = args.strips or max(1, round(ih / (18 * spacing if spacing else 300)))
    cols = args.cols or (max(1, round(iw / (80 * spacing))) if spacing else 1)
    sh, cw = ih / strips, iw / cols
    pad_y, pad_x = (int(sh * 0.25), int(cw * 0.08)) if strips > 1 else (0, int(cw * 0.08))
    for i in range(strips):
        for j in range(cols):
            box = (max(0, left + int(j * cw) - pad_x), max(0, top + int(i * sh) - pad_y),
                   min(W, left + int((j + 1) * cw) + pad_x), min(H, top + int((i + 1) * sh) + pad_y))
            save(img, box, args.out, f"strip{i + 1}" + (f"_col{j + 1}" if cols > 1 else "") + ".png", scale)


if __name__ == "__main__":
    main()
