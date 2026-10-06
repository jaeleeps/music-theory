# music-theory

An [Agent Skill](https://agentskills.io) that works as a study partner for **music theory, analysis, and piano pedagogy** at university and conservatory level, and **draws musical examples on real staves** that you can play back.

- **Theory and analysis**: harmony, Roman numerals and figured bass, voice leading, counterpoint, form. It checks part-writing against a full checklist and reports each problem by bar, beat, and voice.
- **Staff notation**: examples are written in [ABC notation](https://abcnotation.com) and drawn with [abcjs](https://github.com/paulrosen/abcjs): grand staff, SATB on two staves, Roman numerals, figured bass, fingering, dynamics, and a Play button.
- **Practice**: quizzes one question at a time, ear training with hidden answers, and returning to the topics you missed.
- **Pedagogy**: method comparisons, learning theory, lesson plans, practice strategies, repertoire levels, and help with graduate written work. It never invents citations.

![Example: a four-part chorale in B♭ with Roman numerals, and figured bass](assets/example.png)

## Install

**claude.ai (web, desktop, mobile)**: download `music-theory.zip` from the [latest release](https://github.com/jaeleeps/music-theory/releases), or zip the `skills/music-theory/` folder yourself (the zip must contain the `music-theory/` folder). Then go to **Settings → Capabilities → Skills**, upload the zip, and turn it on. Code execution needs to be enabled for skills to work.

**Any agent (Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode, …)**, using the [`skills`](https://github.com/vercel-labs/skills) installer:

```bash
npx skills add jaeleeps/music-theory
npx skills add jaeleeps/music-theory -g     # every project (user scope)
```

**Claude Code plugin:**

```
/plugin marketplace add jaeleeps/music-theory
/plugin install music-theory@music-theory
```

## Usage

Ask in plain language, for example:
- *"Explain the Neapolitan sixth and show me how it resolves in C minor."*
- *"Check my part-writing:"* followed by your chorale in text or a photo of it.
- *"Quiz me on seventh-chord inversions, one at a time."*
- *"Compare the reading approaches of Faber Piano Adventures and The Music Tree."*

In claude.ai, examples appear as an artifact with the staves and a Play button. A red warning box under a staff means the notation has an error, so tell Claude and it will fix it.

## Layout

- `skills/music-theory/`: the skill. Installers copy only this folder.
  - `SKILL.md`: the workflow for teaching, checking, quizzing, and drawing staves.
  - `references/abc-notation.md`: ABC syntax as abcjs renders it, the octave rules, grand staff and SATB layout, and a pre-render checklist.
  - `references/theory.md`: labeling conventions, part-writing and counterpoint checklists, and the analysis procedure.
  - `references/pedagogy.md`: piano pedagogy methods, learning theory, lesson planning, practice, and leveling.
  - `assets/score.html`: the page template that draws and plays the examples.
- `.claude-plugin/`: the Claude Code plugin and marketplace manifests.
- `PRIVACY.md`: privacy policy.

## Renderer

The notation format (ABC) and the renderer (abcjs, loaded in `assets/score.html`) are kept separate, so the renderer can be replaced without rewriting the skill. abcjs 6.7.1 does not support pedal marks or ottava lines. The skill uses text annotations for those instead.

## License

[MIT](LICENSE)
