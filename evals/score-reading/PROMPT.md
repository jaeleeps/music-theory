# Transcription prompt

Each excerpt was given to a fresh Claude Code subagent (Claude Opus 5.5, general-purpose) that had no other context. The prompt is below; `{IMAGE}` and `{RESULT}` are paths. The three conditions differed only in the first rule:

- **clean**: "Read ONLY that image file. Do not open, list, or search any other file or directory, and do not use the web. Work only from what you see." The agents could also zoom with tools; B and C did so (cropping, and in B's case a hand-written PNG decoder to measure notehead positions).
- **photo**: "Read ONLY that image file, by looking at it. Do not run code, write scripts, decode or crop the image programmatically, or measure pixels. …"
- **photo-zoom**: "You SHOULD zoom: make enlarged crops of the image (e.g. one system or a few bars at a time, enlarged 2–4×) and look at those crops. You may use macOS `sips` or Python … do not write code that detects or classifies notes automatically." This condition also added: "Never fill in a note from what the harmony 'should' be; transcribe only what you can see."

```
You are helping test how accurately music notation can be read from an image. Transcribe the score in this image:

{IMAGE}

Rules:
- <condition rule, above>
- Follow this procedure: (1) first read the clef(s), key signature, time signature, and any bar numbers; (2) then transcribe 2–4 bars at a time, staff by staff; (3) apply the key signature and any accidentals that carry through the bar; (4) if you are not sure about a note (pitch, octave, accidental, or rhythm), give your best reading and mark it uncertain instead of skipping it.
- Staves are numbered from the top of each system: 1, 2, ... (on a piano grand staff, 1 = upper staff, 2 = lower). Number measures as printed; if the first bar is an incomplete pickup bar, call it measure 0, otherwise the first bar is 1.
- Pitches in scientific pitch notation with real accidentals: C4 = middle C, e.g. "F#4", "Bb2", "E#5". Write the pitch as it sounds after key signature and accidentals are applied.
- If a staff shows a clef with a small "8" (octave clef) or an 8va line, write the pitch as it sounds.
- Onset = position within the bar in quarter notes, as a fraction string ("0", "1/2", "3/2"). Duration in quarter notes as a fraction string ("1" = quarter, "1/2" = eighth, "3/2" = dotted quarter, "1/3" = eighth-note triplet). For a chord, give one entry per note with the same onset. Skip rests and grace notes. A tied note: list each written note separately.

Write your answer as JSON to {RESULT} in exactly this shape:

{"clefs": ["treble"], "key": "2 sharps", "time": "3/4",
 "notes": [{"measure": 1, "staff": 1, "onset": "0", "pitch": "D4", "dur": "1", "uncertain": false}]}
```
