# .mtext: a plain-text score format

`.mtext` is a plain-text score format from the skill author's music-notation project. Its notation and score-scanning apps export it next to MusicXML. Read this file when the student sends an `.mtext` file or pastes text in this format, or asks for one. It covers the piano and SATB subset that theory and pedagogy work needs.

## Contents
1. Reading it
2. Events and marks
3. Writing it
4. Drawing it on a staff (to ABC)
5. Examples

## 1. Reading it

A file is lines. `%` starts a comment.

| Line | Example | Meaning |
|---|---|---|
| Metadata | `title: Prelude in C` | also `composer`, `subtitle`, `tags`, `source` (`omr` means it came from a scan) |
| Part | `part piano piano name="Piano"` | `part <id> <kind>`. A piano has `staves=treble,bass` by default. Other clefs: `alto`, `tenor`, `treble_8` (octave-down treble) |
| Global | `global \| time=3/4 key=E:minor bpm=60 \| \|` | one segment per bar: meter, key, tempo, and structure |
| Voice | `piano 1.1 \| C4/4 D4 E4 F4 \|` | `<part> <staff>.<voice>`: notes for one voice, bar by bar |
| Lyrics | `piano 1.1 lyrics \| Twin- kle \|` | one syllable per note of that voice |

- **Bars** are separated by `|`. Each line kind keeps its own bar count, so a later `piano 1.1` line continues where the last one stopped. An empty segment means the voice is silent in that bar.
- **Voice numbers are unique within the part, across staves.** On a grand staff, upper-staff voices are `1.1`, `1.2`, and lower-staff voices continue the count: `2.3`, `2.4`. The first number is the staff. The second number names the voice, and it never restarts on staff 2.
- **Global attributes:** `time=4/4`, `time=common`, `time=cut`. `key=G`, `key=G:major`, `key=D:dorian`. `bpm=90`, `beat=4.` (the beat unit), `tempo="Andante"`. `pickup`. `repeat-start`, `repeat-end`, `times=3`. `ending=1`. `barline=double` or `final`. `jump=dc`, `ds`, `fine`, `coda`, `segno`, `dc-al-fine`, `ds-al-coda`, `to-coda`. `break` (a line break in the source).

## 2. Events and marks

**Pitches are written as they sound, with every accidental spelled out**, whatever the key signature: in G major an F-sharp is still `F#4`, and an F-natural is `F4`. Middle C is `C4`. Accidentals are `#`, `##`, `b`, `bb`.

| Token | Meaning |
|---|---|
| `C4/4` | C4, quarter note. `/1` whole, `/2` half, `/8` eighth, `/16` …, `/0` breve. Add a `.` per dot: `/4.` |
| `D4` | **Durations are sticky**: a note without one keeps the voice's previous duration (a quarter at the start). |
| `<C4 E4 G4>/2` | chord |
| `q` | the previous chord again |
| `r/8` | rest. `R` is a whole-bar rest |
| `3{ C4/8 D4 E4 }` | triplet. `5:4{ … }` = 5 in the time of 4 |
| `grace{ D5/16 }` `acc{ D5/16 }` | grace notes. `acc` = acciaccatura (slashed) |
| `C4~` | tie to the next note of the same pitch in this voice (also across a barline) |
| `C4-3` | finger 3. `-4-3` = finger substitution |
| `F#4!` `F#4?` | forced or courtesy accidental |

Marks in brackets come after the duration: `G4/4[p staccato]`. They include dynamics (`pp` … `ff`, `sf`, `sfz`, `fp`), articulations (`staccato`, `staccatissimo`, `tenuto`, `accent`, `marcato`, `portato`), ornaments (`trill`, `mordent`, `inverted-mordent`, `turn`, `inverted-turn`, `tremolo`), `fermata`, `arpeggio`, text in quotes (`"dolce"`, or a Roman numeral `"V7"`), and `staff=2` (a cross-staff note).

Spanners follow the note they attach to: `(` after the first note and `)` after the last for a slur, and `name(` … `)name` for the others, such as `crescendo(`, `diminuendo(`, `pedal(`, `una-corda(`, `ottava-up(`, `phrase(`. `C3/2 pedal( )pedal` holds the pedal for that one note.

Guitar parts add string, fret, and right-hand marks (`B4s1-4+a`). Read them as pitches, and ask the student about the technique marks if they matter.

## 3. Writing it

When the student asks for `.mtext`, write it in this order: metadata, the `part` line, then blocks of a few bars each (a `global` line, then one line per voice), with a blank line between blocks. Then check it:

- every voice's bar adds up to the meter (durations are sticky, so check where they change);
- voice numbers don't repeat across staves (`1.1 1.2 2.3 2.4`, not `2.1`);
- accidentals are spelled out on every note, regardless of the key;
- every `pedal(` and `(` is closed.

The student's apps report syntax errors with line and column, and they report bars that don't add up. If they paste such a message back, fix that spot.

## 4. Drawing it on a staff (to ABC)

To show `.mtext` on a staff, translate it to ABC and use `assets/score.html` (read abc-notation.md first). Most of it maps one-to-one:

| .mtext | ABC (with `L:1/8`) |
|---|---|
| `C4` `C5` `C3` | `C` `c` `C,` |
| `/4` `/8` `/2` `/4.` `/16` | `2` `1` (nothing) `4` `3` `/2` |
| `<C4 E4 G4>/2` | `[CEG]4` |
| `r/4` / `R` | `z2` / `Z` |
| `C4~` | `C-` |
| `C4 ( D4 E4 )` | `(CDE)` |
| `3{ C4/8 D4 E4 }` | `(3CDE` |
| `grace{ D5/16 }` / `acc{ … }` | `{d}` / `{/d}` |
| `[p]` `[staccato]` `[fermata]` | `!p!` `.` `!fermata!` |
| `-3` | `!3!` before the note |
| `["V7"]` on the bass | `"_V⁷"` before the bass note |
| `pedal(` … `)pedal` | `"_Ped."` … `"_*"` (abcjs has no pedal marks) |
| `1.1` `1.2` / `2.3` `2.4` | `V:` voices grouped with `%%score {(S A) \| (T B)}` |

**The one trap is accidentals.** `.mtext` spells every accidental, and ABC applies the key signature. Under `K:G`, `.mtext` `F#4` is ABC `F`, and `.mtext` `F4` is ABC `=F`. An accidental in ABC also carries to the end of the bar, so restate it (`=F`, `^F`) whenever the next note of that letter differs.

Keep the `.mtext` bar numbers in the caption, so the student can compare the staff with their file.

## 5. Examples

A cadence in four voices, with Roman numerals:

```
title: Chorale cadence in C
tags: SATB, part-writing

part choir piano name="SATB" staves=treble,bass

global      | time=4/4 key=C:major | barline=final |
choir 1.1   | E5/4 F5 D5 C5 | C5/1 |
choir 1.2   | C5/4 C5 B4 G4 | G4/1 |
choir 2.3   | G4/4 A4 G4 E4 | E4/1 |
choir 2.4   | C3/4["I"] F3["IV"] G3["V"] C4["I"] | C3/1["I"] |
```

Melody over an Alberti bass, with fingering, a dynamic and a slur:

```
title: Alberti bass in G

part piano piano name="Piano"

global      | time=4/4 key=G:major bpm=96 | |
piano 1.1   | B4-3/2[p] ( C5-4/4 D5-5 ) | B4/2 r/2 |
piano 2.2   | G3-5/8 D4-1 B3-3 D4 G3 D4 B3 D4 | G3/8 D4 B3 D4 G3/2 |
```

Two voices on the upper staff, a tie across the barline, and pedal:

```
title: Two voices and pedal

part piano piano

global      | time=3/4 key=F:major | |
piano 1.1   | A4/4 Bb4 C5~ | C5/2. |
piano 1.2   | F4/2 E4/4 | F4/2. |
piano 2.3   | <F2 C3>/2. pedal( | <F2 C3>/2. )pedal |
```
