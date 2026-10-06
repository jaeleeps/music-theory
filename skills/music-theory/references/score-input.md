# Reading a score the student sends

There are two routes, and they differ a lot in reliability:

| The student sends | Route | Reliability |
|---|---|---|
| A MusicXML file (`.musicxml`, `.xml`, `.mxl`) | Run `scripts/read_musicxml.py`. | **Exact.** Every pitch and rhythm comes from the file itself. |
| A PDF, photo, or screenshot of a score | Zoom with `scripts/zoom.py`, then read the crops visually using the transcription procedure below. | **Good when zoomed, poor when not.** See "Accuracy" below. Always have the student confirm. |

When a passage is long, dense, or important (graded analysis, a lecture-recital), ask whether they have, or can get, a MusicXML version. Many scores on IMSLP and MuseScore.com have one, and any notation program can export one (Finale, Sibelius, Dorico, MuseScore: **File → Export → MusicXML**). Optical music recognition apps (e.g. Audiveris, which is free, or PlayScore) can also convert a clean PDF to MusicXML. Their output has errors too, but the student can correct it in a notation program before sending it.

A PDF exported from notation software is still only a picture of the music for this purpose. Its text layer holds music-font characters, not notes. Treat it like an image.

## Route 1: MusicXML

```bash
python3 scripts/read_musicxml.py score.mxl                  # every note, by measure, staff, and voice
python3 scripts/read_musicxml.py score.mxl --measures 9-16  # only those measures
python3 scripts/read_musicxml.py score.mxl --chords         # all pitches sounding at each onset
```

The path is relative to this skill's folder. Uploaded files are wherever the environment puts them (in claude.ai, usually under `/mnt/user-data/uploads/`). The script needs only Python's standard library.

- The output gives clefs, key, and meter changes, then each measure as `P1 staff 2 v1: @0 Eb3 1/2 + Eb4 1/2 | ...`. `@0` is the onset in quarter notes from the start of the bar, the number after a pitch is its duration in quarter notes, `+` joins the notes of a chord, and `~` marks a tie.
- `--chords` is the input for harmonic analysis. It lists every pitch sounding at each onset, lowest first, including notes held over (attacked notes are marked `*`).
- For a long score, read it a section at a time with `--measures` instead of printing everything.
- Use these pitches as they are. Don't "correct" them from memory of the piece. If the file seems to contradict the edition the student is using, say so.

## Route 2: images and PDFs

### Transcription procedure

1. **Orient first.** Before reading any notes, write down: the clef of every staff, the key signature (count the sharps or flats), the meter, the tempo or character marking, the first bar number, whether the first bar is a pickup, and any clef changes, octave clefs, or 8va lines.
2. **Ask which bars matter.** Transcribe only those. Long transcriptions multiply errors.
3. **Zoom before reading notes. Never transcribe from the whole page.** Make enlarged crops and read those:
   ```bash
   python3 scripts/zoom.py page.jpg --out crops/                  # one strip per system, enlarged 3x
   python3 scripts/zoom.py page.jpg --out crops/ --cols 2         # also split each strip in half
   python3 scripts/zoom.py page.jpg --out crops/ --box 0.5,0,1,0.4   # re-check one region closely
   ```
   For a PDF, first turn the page into an image (e.g. `pdftoppm -r 200 -png score.pdf page`, or Python's `pypdfium2` if it is available). Look at each crop with your image-viewing tool. If a crop is still too small to read with confidence, crop tighter with `--box`. If there is no Python sandbox, ask the student for close-up photos of one system at a time.
4. **Work in small chunks**: 2–4 bars at a time, staff by staff. For each note, decide the line or space, then apply the clef, then the key signature, then any accidental earlier in the same bar.
5. **Count every bar** against the meter. A bar that doesn't add up has a rhythm error.
6. **Mark what you are unsure of**, with a `?` in the text (e.g. `E5?`), instead of guessing silently. Pay most attention to ledger-line notes, accidentals in dense chords, inner and bass voices, and tuplets.
   - **Never fill in a note from what the harmony or style "should" be.** Transcribe only what you can see. If you can't read a note, write `??` and ask. A transcription completed from harmonic expectation turns the analysis into a self-fulfilling guess, and it hides exactly the unusual notes the student most needs to discuss.
7. **Show it back on a staff.** Render the transcription with `assets/score.html`, with the pitches also written out in text, and ask the student to compare it with their score bar by bar. List the notes you marked uncertain.
8. **Analyze only after the student confirms** or corrects the transcription. If they correct a note, update the staff before you go on.

If the image is blurry, cropped, or very dense, ask for a closer crop of the bars in question (one system at a time works best) before transcribing.

### Accuracy

A blind test (2026-10) had Claude transcribe clean engraved excerpts from images, scored against the MusicXML. The results are in [docs/score-reading-test.md](https://github.com/jaeleeps/music-theory/blob/main/docs/score-reading-test.md) in the repository. In short:

| Image | How it was read | Exact notes correct (4 excerpts: melody, Bach chorale, Clara Schumann piano, Joplin piano) |
|---|---|---|
| Clean engraving (like a good PDF) | zoom allowed | 96–100% each |
| Phone-photo quality (small, tilted, blurred) | whole image, no zoom | 91%, 80%, **17%**, **58%** |
| The same phone photos (piano excerpts) | zoomed crops | **100%** and **98%** |

- **Zooming is what makes image reading work.** Without it, dense piano writing on a photo was mostly wrong. With enlarged crops of the same photo, it was nearly perfect.
- Without zoom, the readers filled in notes they couldn't see from the "likely harmony". That is why step 6 forbids it.
- Notes marked uncertain were wrong far more often than notes marked sure, so the uncertainty marks are worth showing the student.
- Caveats: the excerpts were short (4–8 bars) and digitally engraved, two of them are famous (the reader may have recognized them), and real scans of old editions are harder. Treat even a zoomed transcription as a draft for the student to check.

Tell the student roughly what to expect when they send an image of a dense passage, so they check the transcription properly.
