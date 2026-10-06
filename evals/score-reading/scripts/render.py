import sys, re, verovio, os
src, out = sys.argv[1], sys.argv[2]
for k in "ABCD":
    x = open(f"{src}/{k}.musicxml").read()
    # Remove anything that identifies the piece.
    for tag in ["work", "movement-title", "movement-number", "identification", "credit"]:
        x = re.sub(rf"<{tag}\b.*?</{tag}>", "", x, flags=re.S)
    x = re.sub(r"<part-name>.*?</part-name>", "<part-name></part-name>", x)
    tk = verovio.toolkit()
    tk.setOptions({"pageWidth": 2100, "pageHeight": 2970, "adjustPageHeight": True, "scale": 45, "header": "none", "footer": "none"})
    tk.loadData(x)
    assert tk.getPageCount() == 1, (k, tk.getPageCount())
    svg = tk.renderToSVG(1)
    open(f"{out}/{k}.html", "w").write(f'<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">{svg}</body>')
    print(k, "ok", "title-free:", "Music21" not in svg and "mxl" not in svg)
