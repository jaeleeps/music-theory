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

key = json.load(open(sys.argv[1]))
blind = sys.argv[2]
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
    rows.append((k, len(K), len(R), exact, pitch_pos, pitch_only, dict(err), sure_n, sure_ok, unc_n, unc_ok,
                 res.get("key"), res.get("time"), res.get("clefs")))

for (k, nk, nr, ex, pp, po, err, sn, so, un, uo, ks, ts, cl) in rows:
    pct = lambda a, b: f"{100*a/b:.0f}%" if b else "n/a"
    print(f"\n{k}: key notes {nk}, transcribed {nr}   (read key/time/clefs as: {ks} | {ts} | {cl})")
    print(f"  exact (pitch+onset+duration): recall {pct(ex,nk)}, precision {pct(ex,nr)}")
    print(f"  pitch at right onset:         recall {pct(pp,nk)}")
    print(f"  pitch in right bar & staff:   recall {pct(po,nk)}")
    print(f"  pitch errors at right onset:  {err}")
    print(f"  marked sure: {sn} ({pct(so,sn)} exact-correct); marked uncertain: {un} ({pct(uo,un)} exact-correct)")
