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

Each image went to a separate, fresh Claude session (Claude Opus 5.5) with no other context and no access to the answer key. The exact prompt is in [`PROMPT.md`](../evals/score-reading/PROMPT.md). The sessions returned every note as measure, staff, onset, pitch and duration, and flagged each one as sure or uncertain. `grade.py` compared those notes with the key.

## Results

Exact note correctness (right pitch, onset, and duration, in the right bar and staff):

| | A melody | B chorale | C Schumann | D Joplin |
|---|---|---|---|---|
| Clean image | 96%¹ | 100% | 100% | 100% |
| Photo, whole image, no zoom | 91%¹ | 80% | **17%** | **58%** |
| Photo, zoomed crops | — | — | **100%** | **98%** |

¹ One of A's "errors" is a flaw in the test material, not a misreading. The key has a B natural that the engraving draws without a natural sign after a B♭ earlier in the bar, so B♭ is the correct reading of the image. Without that flaw, A scored 100% clean and 96% as a photo.

Notes on the clean round: the B and C sessions zoomed into the image with tools (cropping, and in B's case pixel measurement) without being asked. A and D read it directly.

## Findings

1. **Zooming decides accuracy.** The same phone photo of the Schumann went from 17% to 100%, and the Joplin from 58% to 98%, when the reader looked at enlarged crops instead of the whole image. → The skill now ships `scripts/zoom.py` and requires zooming before any transcription (`references/score-input.md`, step 3).
2. **Without zoom, readers fill gaps from harmony.** Two of the no-zoom photo sessions said outright that some pitches were "filled in from what fits the harmony". For a theory tutor, that is the worst failure: the analysis confirms its own guesses and hides the unusual notes. → The procedure now forbids it and asks for `??` instead.
3. **Uncertainty flags are informative.** In every condition, notes marked *sure* were right 95–100% of the time. Notes marked *uncertain* were right far less often (16–75% in the no-zoom photo round). → The skill shows uncertain notes to the student explicitly.
4. **Inner and lower voices fail first.** In the no-zoom chorale photo, the soprano and alto were 35 of 38 correct, while the bass was 14 of 23.
5. **MusicXML removes the problem.** When a MusicXML file is available, `read_musicxml.py` gives exact notes. The skill asks for one when a passage is long or important.

## Limits of this test

- Short excerpts (4–8 bars), engraved digitally. Real scans of old editions, handwritten scores, and photos with glare or curled pages will be harder.
- B and D are famous, and a reader may have recognized them and recalled notes from memory. C, the least famous, still reached 100% when zoomed.
- One run per condition, so the percentages are indicative, not precise.
- This tested Claude Opus 5.5 in Claude Code. The model behind claude.ai may differ, and claude.ai's image handling may resize uploads differently.

## Re-running

```bash
cd evals/score-reading
pip install music21 verovio pillow           # in a virtualenv
python scripts/make_excerpts.py excerpts      # MusicXML excerpts from the music21 corpus
python scripts/answer_key.py ../../skills/music-theory/scripts/read_musicxml.py excerpts answer_key.json
python scripts/render.py excerpts <dir>       # anonymized HTML pages of each excerpt; screenshot each <svg> to images/clean/score_<X>.png
python scripts/degrade.py images/clean images/photo
# give each image to a fresh session with PROMPT.md, saving results/<condition>/result_<X>.json
python scripts/grade.py answer_key.json results/photo
```
