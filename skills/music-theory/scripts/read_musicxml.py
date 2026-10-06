#!/usr/bin/env python3
"""Print the notes of a MusicXML score as plain text, exactly as written.

Standard library only. Reads .musicxml, .xml and compressed .mxl files
(score-partwise, the format notation programs export).

    python3 read_musicxml.py score.mxl                  # every note, by measure and staff
    python3 read_musicxml.py score.mxl --measures 1-8   # only measures 1 to 8
    python3 read_musicxml.py score.mxl --chords         # all pitches sounding at each onset

Pitches use scientific pitch notation (C4 = middle C). Times and durations are
in quarter notes: "@1" is the second beat of a 4/4 bar, "1/2" is an eighth note.
"""
import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction

KEYS_MAJOR = ["Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#"]
KEYS_MINOR = ["Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#"]
ALTERS = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}
STEP_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def load_root(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            # META-INF/container.xml names the main score file.
            target = None
            if "META-INF/container.xml" in z.namelist():
                container = ET.fromstring(z.read("META-INF/container.xml"))
                # Elements without children are falsy, so compare with None explicitly.
                rootfile = next((e for e in container.iter() if e.tag.split("}")[-1] == "rootfile"), None)
                if rootfile is not None:
                    target = rootfile.get("full-path")
            if target is None:
                target = next(n for n in z.namelist() if n.endswith((".xml", ".musicxml")) and not n.startswith("META-INF"))
            data = z.read(target)
    else:
        with open(path, "rb") as f:
            data = f.read()
    root = ET.fromstring(data)
    if root.tag != "score-partwise":
        sys.exit(f"Unsupported MusicXML root <{root.tag}>: only score-partwise is supported. "
                 "Re-export the score from a notation program as uncompressed or compressed MusicXML.")
    return root


def text(el, path, default=None):
    found = el.find(path)
    return found.text.strip() if found is not None and found.text else default


def fmt_q(q):
    """Format a quarter-note quantity: 1, 1/2, 3/2, 2."""
    q = Fraction(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def pitch_name(step, alter, octave):
    return f"{step}{ALTERS.get(alter, f'{alter:+}')}{octave}"


def midi(step, alter, octave):
    return 12 * (octave + 1) + STEP_SEMITONES[step] + alter


def key_name(fifths, mode):
    i = fifths + 7
    if not 0 <= i < 15:
        return f"{fifths:+} fifths"
    sig = "no sharps or flats" if fifths == 0 else f"{abs(fifths)} {'sharp' if fifths > 0 else 'flat'}{'s' if abs(fifths) > 1 else ''}"
    if mode == "minor":
        return f"{KEYS_MINOR[i]} minor ({sig})"
    if mode == "major":
        return f"{KEYS_MAJOR[i]} major ({sig})"
    return f"{sig}: {KEYS_MAJOR[i]} major or {KEYS_MINOR[i]} minor"


def parse(root):
    """Return (header lines, parts). Each part: dict(name, events, attributes)."""
    header = []
    title = text(root, "work/work-title") or text(root, "movement-title")
    if title:
        header.append(f"Title: {title}")
    for creator in root.findall("identification/creator"):
        if creator.text and creator.text.strip():
            header.append(f"{(creator.get('type') or 'creator').capitalize()}: {creator.text.strip()}")

    names = {sp.get("id"): text(sp, "part-name", sp.get("id")) for sp in root.findall("part-list/score-part")}
    parts = []
    for part in root.findall("part"):
        divisions = 1
        events = []      # dicts: measure, onset, dur, staff, voice, pitch/rest, flags
        attrs = []       # (measure, description)
        for measure in part.findall("measure"):
            mnum = measure.get("number")
            pos = Fraction(0)
            last_onset = Fraction(0)
            for el in measure:
                if el.tag == "attributes":
                    divisions = int(text(el, "divisions", divisions))
                    for key in el.findall("key"):
                        fifths = text(key, "fifths")
                        if fifths is not None:
                            staff = f" (staff {key.get('number')})" if key.get("number") else ""
                            attrs.append((mnum, f"key {key_name(int(fifths), text(key, 'mode'))}{staff}"))
                    for t in el.findall("time"):
                        if t.find("senza-misura") is not None:
                            attrs.append((mnum, "time: unmeasured"))
                        else:
                            beats = "+".join(b.text for b in t.findall("beats"))
                            beat_type = "+".join(b.text for b in t.findall("beat-type"))
                            symbol = f" ({t.get('symbol')})" if t.get("symbol") in ("common", "cut") else ""
                            attrs.append((mnum, f"time {beats}/{beat_type}{symbol}"))
                    staves = text(el, "staves")
                    if staves and staves != "1":
                        attrs.append((mnum, f"{staves} staves"))
                    for clef in el.findall("clef"):
                        sign, line = text(clef, "sign"), text(clef, "line", "")
                        octave = text(clef, "clef-octave-change")
                        shift = f" {int(octave):+} octave" if octave else ""
                        staff = f" (staff {clef.get('number', '1')})"
                        attrs.append((mnum, f"clef {sign}{line}{shift}{staff}"))
                elif el.tag == "backup":
                    pos -= Fraction(int(text(el, "duration", 0)), divisions)
                elif el.tag == "forward":
                    pos += Fraction(int(text(el, "duration", 0)), divisions)
                elif el.tag == "note":
                    is_chord = el.find("chord") is not None
                    is_grace = el.find("grace") is not None
                    dur = Fraction(int(text(el, "duration", 0)), divisions) if not is_grace else Fraction(0)
                    onset = last_onset if is_chord else pos
                    ev = {
                        "measure": mnum, "onset": onset, "dur": dur,
                        "staff": int(text(el, "staff", 1)), "voice": text(el, "voice", "1"),
                        "grace": is_grace, "tie_start": False, "tie_stop": False, "tuplet": None,
                    }
                    p = el.find("pitch")
                    if p is not None:
                        step, alter, octave = text(p, "step"), int(float(text(p, "alter", 0))), int(text(p, "octave"))
                        ev["pitch"] = pitch_name(step, alter, octave)
                        ev["midi"] = midi(step, alter, octave)
                    elif el.find("unpitched") is not None:
                        u = el.find("unpitched")
                        ev["pitch"] = f"unpitched {text(u, 'display-step', '?')}{text(u, 'display-octave', '')}"
                        ev["midi"] = None
                    else:
                        ev["pitch"] = None  # rest
                        ev["midi"] = None
                    for tie in el.findall("tie"):
                        ev["tie_" + tie.get("type")] = True
                    tm = el.find("time-modification")
                    if tm is not None:
                        ev["tuplet"] = f"{text(tm, 'actual-notes')}:{text(tm, 'normal-notes')}"
                    events.append(ev)
                    if not is_chord:
                        last_onset = pos
                        pos += dur
        parts.append({"name": names.get(part.get("id"), part.get("id")), "events": events, "attrs": attrs})
    return header, parts


def in_range(mnum, lo, hi):
    try:
        n = int("".join(ch for ch in mnum if ch.isdigit()) or 0)
    except ValueError:
        return True
    return (lo is None or n >= lo) and (hi is None or n <= hi)


def measure_order(parts):
    seen = []
    for part in parts:
        for ev in part["events"]:
            if ev["measure"] not in seen:
                seen.append(ev["measure"])
    return seen


def note_label(ev):
    if ev["pitch"] is None:
        s = f"rest {fmt_q(ev['dur'])}"
    else:
        s = ev["pitch"] + ("(grace)" if ev["grace"] else f" {fmt_q(ev['dur'])}")
    if ev["tie_stop"]:
        s = "~" + s
    if ev["tie_start"]:
        s += "~"
    if ev["tuplet"]:
        s += f" [{ev['tuplet']}]"
    return s


def print_notes(header, parts, lo, hi):
    for line in header:
        print(line)
    print("Notation: C4 = middle C. '@x' = onset in quarter notes from the start of the bar; "
          "numbers after a pitch = duration in quarter notes; '~' = tie; '[3:2]' = tuplet.")
    for i, part in enumerate(parts, 1):
        print(f"\nPart {i}: {part['name']}")
        for mnum, desc in part["attrs"]:
            if in_range(mnum, lo, hi) or mnum == part["attrs"][0][0]:
                print(f"  m.{mnum}: {desc}")
    for mnum in measure_order(parts):
        if not in_range(mnum, lo, hi):
            continue
        print(f"\nm.{mnum}")
        for i, part in enumerate(parts, 1):
            evs = [e for e in part["events"] if e["measure"] == mnum]
            for staff in sorted({e["staff"] for e in evs}):
                for voice in sorted({e["voice"] for e in evs if e["staff"] == staff}, key=str):
                    group = [e for e in evs if e["staff"] == staff and e["voice"] == voice]
                    by_onset = {}
                    for e in group:
                        by_onset.setdefault(e["onset"], []).append(e)
                    cells = []
                    for onset in sorted(by_onset):
                        notes = sorted(by_onset[onset], key=lambda e: (e["midi"] is None, e["midi"] or 0))
                        cells.append(f"@{fmt_q(onset)} " + " + ".join(note_label(e) for e in notes))
                    label = f"P{i}" + (f" staff {staff}" if len({e['staff'] for e in part['events']}) > 1 else "") + f" v{voice}"
                    print(f"  {label}: " + " | ".join(cells))


def print_chords(header, parts, lo, hi):
    for line in header:
        print(line)
    print("Each line: onset in quarter notes from the start of the bar, then every pitch sounding at that moment "
          "(including notes held over), lowest first. '*' marks notes attacked at that onset.")
    for mnum in measure_order(parts):
        if not in_range(mnum, lo, hi):
            continue
        evs = [e for p in parts for e in p["events"] if e["measure"] == mnum and e["midi"] is not None and not e["grace"]]
        print(f"\nm.{mnum}")
        for onset in sorted({e["onset"] for e in evs}):
            sounding = [e for e in evs if e["onset"] <= onset < e["onset"] + e["dur"]]
            sounding.sort(key=lambda e: e["midi"])
            names = [("*" if e["onset"] == onset and not e["tie_stop"] else "") + e["pitch"] for e in sounding]
            print(f"  @{fmt_q(onset)}: " + " ".join(names))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--measures", help="range such as 1-8, 5, or 12-")
    ap.add_argument("--chords", action="store_true", help="list all pitches sounding at each onset")
    args = ap.parse_args()
    lo = hi = None
    if args.measures:
        a, _, b = args.measures.partition("-")
        lo = int(a) if a else None
        hi = (int(b) if b else None) if "-" in args.measures else lo
    try:
        header, parts = parse(load_root(args.file))
    except FileNotFoundError:
        sys.exit(f"File not found: {args.file}")
    except (ET.ParseError, zipfile.BadZipFile, StopIteration, KeyError) as e:
        sys.exit(f"Not a readable MusicXML file ({type(e).__name__}: {e}). "
                 "Export the score from a notation program as MusicXML (.musicxml or .mxl).")
    (print_chords if args.chords else print_notes)(header, parts, lo, hi)


if __name__ == "__main__":
    main()
