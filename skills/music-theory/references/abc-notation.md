# ABC notation for this skill

Everything here was checked against abcjs 6.7.1, the renderer that `assets/score.html` loads. If a construct is not listed, assume it is untested: prefer a listed alternative, and if you use it anyway, tell the student it may not render.

## Contents
1. Header fields
2. Pitch and octave (most errors start here)
3. Accidentals and key signatures
4. Duration and rhythm
5. Chords, ties, slurs, beams
6. Multiple voices: grand staff and SATB
7. Text under and over the staff: Roman numerals, figured bass, labels
8. Piano and expressive markings
9. Unsupported in abcjs, and what to do instead
10. Pre-render checklist

## 1. Header fields

```
X:1            reference number, first line of every tune
T:Title        optional; the template already shows a title, so usually omit
M:4/4          meter (C and C| also work)
L:1/8          default note length
Q:1/4=80       tempo; the template's Play button reads the number after "="
K:G            key, always the LAST header line
```

## 2. Pitch and octave

Scientific pitch notation: C4 is middle C.

| ABC | Pitch | ABC | Pitch |
|---|---|---|---|
| `C,,` | C2 | `C` | C4 (middle C) |
| `C,` | C3 | `c` | C5 |
| `G,` | G3 | `c'` | C6 |
| `B,` | B3 | `c''` | C7 |

- Uppercase letters `C`–`B` are octave 4. Lowercase `c`–`b` are octave 5. Each `,` lowers an octave, and each `'` raises one.
- The octave changes at C, not at A. `B,` (B3) sits just below `C` (C4), and `B` (B4) just below `c` (C5).
- The clef never changes the pitch an ABC letter means. `C` is middle C in treble, bass and alto clef alike. So a bass-staff part almost always needs commas: the bass staff's middle line is `D,`, its bottom line is `G,,`, and its top line is `A,`.
- Typical SATB ranges in ABC: soprano `C`–`g` (C4–G5), alto `G,`–`d` (G3–D5), tenor `C,`–`g` (C3–G4), bass `E,,`–`d` (E2–D4). Tenor is the voice most often written an octave too high: tenor middle C is `C`, and most tenor notes have one comma.

## 3. Accidentals and key signatures

- `^` sharp, `_` flat, `=` natural, `^^` double sharp, `__` double flat. They go before the letter: `^F`, `_B,`, `=c`.
- `K:` applies the key signature. In `K:D`, a plain `F` sounds as F♯. Write `=F` for F natural.
- An accidental lasts until the barline, for that pitch in that octave, the same as in printed music. Re-state it in the next bar if needed.
- Keys: `K:C`, `K:Bb`, `K:F#`, `K:Am` (A minor), `K:C#m`, and modes such as `K:D dor`, `K:G mix`. Write the harmonic minor's raised seventh explicitly: in `K:Am`, write the leading tone as `^G`.
- `K:C` with explicit accidentals is fine for atonal or chromatic examples.

## 4. Duration and rhythm

Durations are multiples of `L:`. With `L:1/8`:

| ABC | Value | ABC | Value |
|---|---|---|---|
| `C` | eighth | `C/` or `C/2` | sixteenth |
| `C2` | quarter | `C3` | dotted quarter |
| `C4` | half | `C6` | dotted half |
| `C8` | whole | `z2` | quarter rest |
| `C16` | breve (double whole) | `C//` or `C/4` | thirty-second |
| `C7`, with `L:1/16` | double-dotted quarter | `C/8` | sixty-fourth |

- `>` means the first note is dotted and the second shortened: `c>d` is a dotted eighth plus a sixteenth. `<` is the reverse.
- Triplet: `(3abc` fits three notes into the time of two.
- Rests: `z` (with a length, e.g. `z4`). A full-bar rest is `Z`. A multi-bar rest is `Z4` (drawn as one rest with "4" above it).
- Meters: `M:C` is common time and `M:C|` is cut time (both draw the C symbols). Change meter mid-piece with an inline field: `[M:3/4]`.
- **Every bar must add up to the meter.** Count each bar before rendering (see section 10). abcjs does not warn about a bar that is too short or too long.

## 5. Chords, ties, slurs, beams

- Chord: `[CEG]` (a block chord in one voice). The length goes after the bracket: `[CEG]2`.
- Tie: `c2-c2`. A tie joins same-pitch notes only.
- Slur: `(cdef)`.
- Notes written with no space between them are beamed: `cdef` is one beamed group, `cd ef` is two.
- Barlines: `|`, final `|]`, double `||`, repeats `|:` and `:|`, first and second endings `|1` and `:|2`. There is no dotted barline: `.|` is misread as a staccato dot, without a warning.

## 6. Multiple voices: grand staff and SATB

Declare each voice with `V:` lines after `K:`, and group them with `%%score` (put `%%score` before `K:`). Curly braces `{}` draw a piano brace. Round brackets `()` put two voices on one staff.

Piano grand staff:
```
X:1
M:4/4
L:1/4
%%score {RH | LH}
K:C
V:RH clef=treble
V:LH clef=bass
[V:RH] e d c2 |]
[V:LH] C, G,, C,2 |]
```

Four-part chorale (SATB on two staves, stems separating the voices):
```
X:1
M:3/4
L:1/4
%%score {(S A) | (T B)}
K:Bb
V:S clef=treble stems=up
V:A clef=treble stems=down
V:T clef=bass stems=up
V:B clef=bass stems=down
[V:S] d e d | c3 | B3 |]
[V:A] B B B | A3 | B3 |]
[V:T] F, G, F, | E,3 | D,3 |]
[V:B] B,, B,, B,, | F,,3 | B,,3 |]
```

- Each voice must have the same number of bars, and each bar must be complete in every voice.
- Other clefs: `clef=alto` and `clef=tenor` render correctly.

## 7. Text under and over the staff

An annotation is a quoted string placed just before a note. `"_text"` goes below the staff and `"^text"` above it. A string with no `^` or `_` is read as a chord symbol and drawn above the staff.

- **Roman numerals**: put them under the lowest voice with `"_..."`. Use Unicode superscripts and subscripts for figures: `"_V⁷"`, `"_IV⁶₄"`, `"_V⁶₅"`, `"_V⁴₃"`, `"_V⁴₂"`, `"_vii°⁷"`, `"_viiø⁷"`, `"_V⁷/V"`. Characters: ⁰¹²³⁴⁵⁶⁷⁸⁹ and ₀₁₂₃₄₅₆₇₈₉.
- **Figured bass**: stack figures with a literal backslash-n: `"_6\n4"D,`. Inside `assets/score.html` the ABC sits in a text/vnd.abc script element, which keeps the backslash as typed. If you ever put ABC inside a JavaScript string instead, a `\n` becomes a real line break and breaks the parse.
- **Chord symbols** for lead sheets and jazz: `"Cmaj7"C`, `"G7"G,`.
- **Analytical labels**: `"^P5!"`, `"^NCT"`, `"^PT"` (passing tone), `"^S"`/`"^A"` (sentence and phrase labels, Caplin's terms), and so on. Short labels read best.
- Lyrics: a `w:` line under a voice line puts one syllable under each note of that voice. Annotations are usually easier to control for analysis.

## 8. Piano and expressive markings

| Marking | ABC |
|---|---|
| Fingering | `!1!c !2!d !3!e` |
| Dynamics | `!pp! !p! !mp! !mf! !f! !ff! !sfz!` |
| Hairpins | `!crescendo(! … !crescendo)!`, `!diminuendo(! … !diminuendo)!` |
| Staccato | `.c` |
| Accent | `!accent!c` |
| Tenuto | `!tenuto!c` |
| Fermata | `!fermata!c` |
| Trill | `!trill!c` (or `!tr!c`) |
| Upper mordent (no line; *Pralltriller*) | `!uppermordent!c` or `!pralltriller!c` |
| Lower mordent (with line) | `!lowermordent!c` or `!mordent!c` |
| Turn | `!turn!c` |
| Staccatissimo (wedge) | `!wedge!c` |
| Strong marcato (^) | `!^!c` or `!marcato!c` |
| Arpeggiated chord | `!arpeggio![CEGc]` |
| Glissando | `!glissando(!C2 !glissando)!c2` (the line runs from the first note to the second) |
| Tremolo, one note | `!/!c`, `!//!c`, `!///!c` (1–3 slashes on the stem) |
| Breath mark | `!breath!c` |
| Segno, coda | `!segno!c`, `!coda!c` |
| D.C., D.S., Fine | `!D.C.!c`, `!D.S.!c`, `!fine!c`, `!D.C.alfine!c`, `!D.S.alcoda!c` |
| Softest and loudest | `!ppp!`, `!pppp!`, `!fff!`, `!ffff!` |
| Appoggiatura (unslashed grace note) | `{B}c`, or several: `{AB}c` |
| Acciaccatura (slashed grace note) | `{/B}c`, or several: `{/AB}c` |

## 9. Unsupported in abcjs, and what to do instead

| Wanted | Not supported | Use instead |
|---|---|---|
| Pedal marks | `!ped!`, `!ped-up!` | annotations `"_Ped."` and `"_*"` |
| Ottava line | `!8va(!` … `!8va)!` | write the real pitches with ledger lines, or the annotation `"^8va"` plus a caption |
| *fp* | `!fp!` | the annotation `"_fp"` |
| Inverted turn | `!invertedturn!`, `!turnx!` (**no warning, nothing drawn**) | write the notes out, or a caption |
| Tremolo between two notes | `!trem1!`–`!trem4!` (**no warning, nothing drawn**) | write the notes out, or a caption ("measured tremolo between C and E") |
| Simile (repeat-beat or repeat-bar sign) | none | write the music out |
| Dotted barline | `.\|` (**misread as staccato, no warning**) | a plain `\|` plus a caption |
| Editorial or courtesy accidental in brackets | `!editorial!`, `!courtesy!` (draw a plain accidental) | a plain accidental, plus a caption noting it is a courtesy accidental |

If the template shows a red "Notation warnings" box, the ABC has an error. Fix it before showing the example to the student. The rows marked **no warning** fail silently, so the warning box cannot catch them. Never use them.

**Crowding:** text marks on neighboring notes overlap (e.g. `!D.S.!` next to `!D.S.alcoda!`, or a new dynamic on every note). Put at most one text mark on any two consecutive notes, or put the marks on different sides of the staff (`"^…"` and `"_…"`).

## 10. Pre-render checklist

Do this in your reasoning, every time, before the ABC goes into the template:

1. **Spell the pitches in words first** in scientific pitch notation, voice by voice (e.g. "S: D5 E♭5 D5 | C5 | B♭4"). Check the music itself at this stage: voice leading, chord members, ranges.
2. **Translate to ABC** using the octave table, and re-check every octave mark. Bass and tenor parts usually need commas.
3. **Check accidentals against the key signature.** Is any note affected by the key signature that should not be? Is an accidental still active later in the same bar?
4. **Count every bar in every voice** against `M:` and `L:`.
5. **Check that the voices line up**: the same number of bars, and simultaneous notes at the same beat.
6. Also show the pitches in text under the staff (`<p class="notes">`), so the student can check the notation and you can both talk about specific notes.
