import json, sys, re
from collections import Counter
from fractions import Fraction

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

def norm_pitch(p):
    p = p.strip().replace("♭", "b").replace("♯", "#").replace("-", "b").replace("x", "##")
    m = re.fullmatch(r"([A-Ga-g])(bb|b|##|#|n)?(-?\d)", p)
    if not m:
        return None
    acc = (m.group(2) or "").replace("n", "")
    return f"{m.group(1).upper()}{acc}{m.group(3)}"

def midi(p):
    m = re.fullmatch(r"([A-G])(bb|b|##|#)?(-?\d)", p)
    a = {"": 0, "b": -1, "bb": -2, "#": 1, "##": 2}[m.group(2) or ""]
    return 12 * (int(m.group(3)) + 1) + STEP[m.group(1)] + a

def frac(s):
    try:
        return Fraction(str(s))
    except Exception:
        return None

def meter_length(k):
    """Bar length in quarter notes, from the excerpt's first time signature."""
    xml = open(f"{EXCERPTS}/{k}.musicxml").read()
    beats, beat_type = re.search(r"<beats>(\d+)</beats>", xml), re.search(r"<beat-type>(\d+)</beat-type>", xml)
    return Fraction(4 * int(beats.group(1)), int(beat_type.group(1)))

def timeline(notes, key_notes, bar):
    """(onset from the start of the excerpt, MIDI pitch), in playing order. A pickup
    bar (measure 0) is as long as the answer key's notes in it."""
    pickup = max((o + d for m, s, o, p, d in key_notes if m == 0), default=Fraction(0))
    start = lambda m: Fraction(0) if m == 0 else pickup + (m - 1) * bar
    return sorted((start(m) + o, midi(p)) for m, s, o, p, d in notes)

def lcs_rhythm(expected, recognized):
    """Pitch F1 over the longest common subsequence, and the rhythm score on the
    matched notes: the share whose distance from the previous matched note is the
    same on both sides. Ported from music-web's scripts/accuracy.ts, so a missed
    or extra note costs one note, not every note after it."""
    a, b = [p for _, p in expected], [p for _, p in recognized]
    w = len(b) + 1
    t = [0] * ((len(a) + 1) * w)
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            t[i * w + j] = t[(i - 1) * w + j - 1] + 1 if a[i - 1] == b[j - 1] else max(t[(i - 1) * w + j], t[i * w + j - 1])
    pairs, i, j = [], len(a), len(b)
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1] and t[i * w + j] == t[(i - 1) * w + j - 1] + 1:
            i, j = i - 1, j - 1
            pairs.append((i, j))
        elif t[(i - 1) * w + j] >= t[i * w + j - 1]:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    kept = sum(1 for (i0, j0), (i1, j1) in zip(pairs, pairs[1:])
               if expected[i1][0] - expected[i0][0] == recognized[j1][0] - recognized[j0][0])
    n = len(pairs)
    precision, recall = (n / len(b) if b else 0), (n / len(a) if a else 0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return f1, (kept / (n - 1) if n > 1 else n)

key = json.load(open(sys.argv[1]))
blind = sys.argv[2]
EXCERPTS = sys.argv[3] if len(sys.argv) > 3 else "excerpts"
rows = []
for k in "ABCD":
    try:
        res = json.load(open(f"{blind}/result_{k}.json"))
    except Exception as e:
        print(k, "no result:", e); continue
    K = [(m, s, Fraction(o), p, Fraction(d)) for m, s, o, p, d in key[k]]
    R, unc = [], []
    for n in res.get("notes", []):
        p = norm_pitch(str(n.get("pitch", "")))
        o, d = frac(n.get("onset")), frac(n.get("dur"))
        if p is None or o is None or d is None:
            continue
        R.append((int(n["measure"]), int(n["staff"]), o, p, d)); unc.append(bool(n.get("uncertain")))
    kc, rc = Counter(K), Counter(R)
    exact = sum((kc & rc).values())
    pos = lambda xs: Counter(x[:4] for x in xs)
    pitch_pos = sum((pos(K) & pos(R)).values())
    pcls = lambda xs: Counter((x[0], x[1], x[3]) for x in xs)
    pitch_only = sum((pcls(K) & pcls(R)).values())
    # classify pitch errors among notes at a matching (measure, staff, onset)
    kleft = list((pos(K) - pos(R)).elements()); rleft = list((pos(R) - pos(K)).elements())
    err = Counter()
    for kn in kleft:
        cands = [r for r in rleft if r[:3] == kn[:3]]
        if not cands:
            err["missed/misplaced"] += 1; continue
        r = min(cands, key=lambda r: abs(midi(r[3]) - midi(kn[3]))); rleft.remove(r)
        kp, rp = kn[3], r[3]
        if kp[0] == rp[0] and kp[-1] != rp[-1] and kp[1:-1] == rp[1:-1]: err["octave"] += 1
        elif kp[0] == rp[0] and kp[-1] == rp[-1]: err["accidental"] += 1
        else: err["wrong letter"] += 1
    # were uncertain flags informative?
    correct_set = kc.copy(); sure_ok = sure_n = unc_ok = unc_n = 0
    for x, u in zip(R, unc):
        ok = correct_set[x] > 0
        if ok: correct_set[x] -= 1
        if u: unc_n += 1; unc_ok += ok
        else: sure_n += 1; sure_ok += ok
    bar = meter_length(k)
    f1, rhythm = lcs_rhythm(timeline(K, K, bar), timeline(R, K, bar))
    rows.append((k, len(K), len(R), exact, pitch_pos, pitch_only, dict(err), sure_n, sure_ok, unc_n, unc_ok,
                 res.get("key"), res.get("time"), res.get("clefs"), f1, rhythm))

for (k, nk, nr, ex, pp, po, err, sn, so, un, uo, ks, ts, cl, f1, rhythm) in rows:
    pct = lambda a, b: f"{100*a/b:.0f}%" if b else "n/a"
    print(f"\n{k}: key notes {nk}, transcribed {nr}   (read key/time/clefs as: {ks} | {ts} | {cl})")
    print(f"  exact (pitch+onset+duration): recall {pct(ex,nk)}, precision {pct(ex,nr)}")
    print(f"  pitch at right onset:         recall {pct(pp,nk)}")
    print(f"  pitch in right bar & staff:   recall {pct(po,nk)}")
    print(f"  pitch errors at right onset:  {err}")
    print(f"  in playing order (LCS):       pitch F1 {100*f1:.0f}%, rhythm {100*rhythm:.0f}%")
    print(f"  marked sure: {sn} ({pct(so,sn)} exact-correct); marked uncertain: {un} ({pct(uo,un)} exact-correct)")
