import sys, os
from music21 import corpus, converter
out = sys.argv[1]
specs = {
  "A": ("essenFolksong/altdeu10.abc", 1, 8),
  "B": ("bach/bwv66.6.mxl", 0, 4),
  "C": ("schumann_clara/polonaise_op1n1.mxl", 1, 6),
  "D": ("joplin/maple_leaf_rag.mxl", 1, 6),
}
for k,(path,a,b) in specs.items():
    s = corpus.parse(path)
    if hasattr(s, 'scores'):  # opus
        s = s.scores[0]
    ex = s.measures(a, b)
    fn = ex.write('musicxml', fp=os.path.join(out, f"{k}.musicxml"))
    print(k, path, "parts:", len(ex.parts), "->", fn)
