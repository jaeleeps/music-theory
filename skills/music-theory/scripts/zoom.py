#!/usr/bin/env python3
"""Cut a score image into enlarged crops, so notes can be read up close.

Reading a whole page at once is unreliable; reading enlarged crops is not
(see references/score-input.md). Needs Pillow (preinstalled in most Python
sandboxes, including claude.ai's code execution).

    python3 zoom.py page.jpg --out crops/                    # horizontal strips (about one system each)
    python3 zoom.py page.jpg --out crops/ --strips 4 --cols 2   # 4 strips, each split in 2 halves
    python3 zoom.py page.jpg --out crops/ --box 0,0.5,0.5,1     # one region: left,top,right,bottom as fractions

Each crop overlaps its neighbours slightly, is enlarged (default 3x), and is
sharpened. Then look at the crops one at a time.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    sys.exit("Pillow is not installed (pip install pillow). Without it, ask the student for a closer, "
             "higher-resolution photo of one system at a time instead.")


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
    ap.add_argument("--strips", type=int, default=0, help="horizontal strips (default: about one per 300 px of height)")
    ap.add_argument("--cols", type=int, default=1, help="split each strip into this many columns")
    ap.add_argument("--box", help="single region as fractions: left,top,right,bottom")
    ap.add_argument("--scale", type=float, default=3.0, help="enlargement factor (default 3)")
    args = ap.parse_args()

    try:
        img = ImageOps.exif_transpose(Image.open(args.image)).convert("L")
    except (FileNotFoundError, OSError) as e:
        sys.exit(f"Cannot open image: {e}")
    os.makedirs(args.out, exist_ok=True)
    W, H = img.size

    if args.box:
        l, t, r, b = (float(v) for v in args.box.split(","))
        if not (0 <= l < r <= 1 and 0 <= t < b <= 1):
            sys.exit("--box needs 0 <= left < right <= 1 and 0 <= top < bottom <= 1")
        save(img, (int(l * W), int(t * H), int(r * W), int(b * H)), args.out, "box.png", args.scale)
        return

    strips = args.strips or max(1, round(H / 300))
    sh, cw = H / strips, W / args.cols
    pad_y, pad_x = int(sh * 0.12), int(cw * 0.08)   # overlap so no note is cut in half at a crop edge
    for i in range(strips):
        for j in range(args.cols):
            box = (max(0, int(j * cw) - pad_x), max(0, int(i * sh) - pad_y),
                   min(W, int((j + 1) * cw) + pad_x), min(H, int((i + 1) * sh) + pad_y))
            save(img, box, args.out, f"strip{i + 1}" + (f"_col{j + 1}" if args.cols > 1 else "") + ".png", args.scale)


if __name__ == "__main__":
    main()
