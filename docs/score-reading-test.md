# How well can Claude read notation from an image?

A blind test, run 2026-10-05, to decide how the skill should handle scores that students send as PDFs or photos. The materials and scripts are in [`evals/score-reading/`](../evals/score-reading/).

## Setup

Four excerpts from the [music21](https://github.com/cuthbertLab/music21) corpus, all public-domain music:

| | Excerpt | Bars | Notes | What makes it hard |
|---|---|---|---|---|
| A | German folk song (Essen collection, `altdeu10`) | 8 | 23 | single line, but 4/2 meter and accidentals that carry through the bar |
| B | Bach, chorale BWV 66.6 | pickup + 4 | 84 | four staves (SATB), F♯ minor |
| C | Clara Schumann, Polonaise Op. 1 No. 1 | 6 | 124 | piano: chords, triplet runs up to E♭7, a clef change to an octave treble clef |
| D | Joplin, *Maple Leaf Rag* | 6 | 98 | piano: dense chords, syncopation, A♭ major |

Each excerpt was exported to MusicXML, which serves as the answer key, read with the skill's own `read_musicxml.py`. That reader matched music21's parse of the same files exactly (494 of 494 notes, including the full compressed BWV 66.6 file). Each excerpt was then engraved with [Verovio](https://www.verovio.org), with titles and composer names removed, and saved in two versions:
- **clean**: a crisp PNG, like a good PDF page;
- **photo**: about half the resolution, tilted 1.2°, blurred, on grey paper, saved as a low-quality JPEG, like a phone photo of a printed page.
- **phone** (added 2026-11): a phone shot of the page lying on a dark table. The page is bent (a slight wave), seen at a slant, lit unevenly with a soft corner shadow, blurred and noisy, JPEG 85, with a staff spacing of about 6 px. The noise is seeded, so `degrade.py` always makes the same images. The design follows the `phone` variant in the author's music-web optical-recognition tests.

Each image went to a separate, fresh Claude session (Claude Opus 5.5) with no other context and no access to the answer key. The exact prompt is in [`PROMPT.md`](../evals/score-reading/PROMPT.md). The sessions returned every note as measure, staff, onset, pitch and duration, and flagged each one as sure or uncertain. `grade.py` compared those notes with the key.

## Results

Exact note correctness (right pitch, onset, and duration, in the right bar and staff):

| | A melody | B chorale | C Schumann | D Joplin |
|---|---|---|---|---|
| Clean image | 96%¹ | 100% | 100% | 100% |
| Photo, whole image, no zoom | 91%¹ | 80% | **17%** | **58%** |
| Photo, zoomed crops | — | — | **100%** | **98%** |
| Phone shot, straightened (`--corners`), then zoomed | 96%¹ | 100% | 92% | 100% |
| The same, with the revised `zoom.py` (re-run of C) | | | **100%** | |

¹ One of A's "errors" is a flaw in the test material, not a misreading. The key has a B natural that the engraving draws without a natural sign after a B♭ earlier in the bar, so B♭ is the correct reading of the image. Without that flaw, A scored 100% clean, 96% as a photo, and 100% as a phone shot.

`grade.py` also scores each result the way music-web's sample evaluation does. **Pitch F1** counts the notes in the longest common subsequence of the two pitch lists in playing order, so a missed or extra note costs one note, not every note after it. **Rhythm** is the share of matched notes whose distance from the previous matched note is right, so a misread meter or lost triplets show up even when the pitches are right. It shows how much worse the no-zoom photo round was: C kept only 48% of its rhythm and D 70%, while every zoomed or phone run kept 95–100%.

Notes on the clean round: the B and C sessions zoomed into the image with tools (cropping, and in B's case pixel measurement) without being asked. A and D read it directly.

## Findings

1. **Zooming decides accuracy.** The same phone photo of the Schumann went from 17% to 100%, and the Joplin from 58% to 98%, when the reader looked at enlarged crops instead of the whole image. → The skill now ships `scripts/zoom.py` and requires zooming before any transcription (`references/score-input.md`, step 3).
2. **Without zoom, readers fill gaps from harmony.** Two of the no-zoom photo sessions said outright that some pitches were "filled in from what fits the harmony". For a theory tutor, that is the worst failure: the analysis confirms its own guesses and hides the unusual notes. → The procedure now forbids it and asks for `??` instead.
3. **Uncertainty flags are informative.** In every condition, notes marked *sure* were right 95–100% of the time. Notes marked *uncertain* were right far less often (16–75% in the no-zoom photo round). → The skill shows uncertain notes to the student explicitly.
4. **Inner and lower voices fail first.** In the no-zoom chorale photo, the soprano and alto were 35 of 38 correct, while the bass was 14 of 23.
5. **Phone shots work once the page is straightened.** The readers looked at the photo, estimated the page corners by eye, and straightened it with `zoom.py --corners`. That reached 92–100% in the first round, and the rhythm was right throughout. C's ten misses were two-note chords read one step off, where two blurred noteheads look like one, and 7 of the 10 were marked uncertain. All four readers asked for more detail: on the 1× straightened page, staff lines about 6 px apart stayed blurry even at 10–14× zoom. `zoom.py` now straightens at twice the photo's resolution, enlarges crops to about 40 px staff spacing (the readers had set 40–80 px by hand), sizes the default crops from the staff spacing, and no longer overwrites earlier `--box` crops. Three readers found `--flatten` made the paper grainier and dropped it for close-ups, which the skill now advises. A fresh blind session then re-ran C with the revised script and scored 100% (124 of 124 notes, rhythm 100%). It didn't need `--flatten`. It still enlarged single bars to 9–12× by hand, read narrow `--box` crops because its corner estimate left the page about 1–2° rotated, and found the passages with five or six ledger lines the hardest.
6. **MusicXML removes the problem.** When a MusicXML file is available, `read_musicxml.py` gives exact notes. The skill asks for one when a passage is long or important.

## Limits of this test

- Short excerpts (4–8 bars), engraved digitally. Real scans of old editions, handwritten scores, and photos with glare or curled pages will be harder.
- B and D are famous, and a reader may have recognized them and recalled notes from memory. C, the least famous, still reached 100% when zoomed.
- One run per condition (two for C as a phone shot: 92%, then 100% with the revised script), so the percentages are indicative, not precise.
- This tested Claude Opus 5.5 in Claude Code. The model behind claude.ai may differ, and claude.ai's image handling may resize uploads differently.

## Re-running

```bash
cd evals/score-reading
pip install music21 verovio pillow           # in a virtualenv
python scripts/make_excerpts.py excerpts      # MusicXML excerpts from the music21 corpus
python scripts/answer_key.py ../../skills/music-theory/scripts/read_musicxml.py excerpts answer_key.json
python scripts/render.py excerpts <dir>       # anonymized HTML pages of each excerpt; screenshot each <svg> to images/clean/score_<X>.png
python scripts/degrade.py images/clean images/photo
python scripts/degrade.py images/clean images/phone phone
# give each image to a fresh session with PROMPT.md, saving results/<condition>/result_<X>.json
python scripts/grade.py answer_key.json results/photo
```
