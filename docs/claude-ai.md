# Using music-theory in claude.ai

This guide is for using the skill on the Claude website ([claude.ai](https://claude.ai)) or in the Claude desktop and mobile apps. You don't need to install anything on your computer.

## 1. Turn on code execution (one time)

Skills only work when Claude can run code.

- **Free, Pro, or Max plan**: open [Settings → Capabilities](https://claude.ai/settings/capabilities) and turn on **Code execution and file creation**.
- **Team or Enterprise plan**: an admin has to turn on **Cloud code execution and file creation** and **Skills** in [Organization settings → Plugins & skills](https://claude.ai/admin-settings/skills) (the **Policy** tab).

## 2. Download the skill

Download **`music-theory.zip`** from the [latest release](https://github.com/jaeleeps/music-theory/releases/latest). Don't unzip it.

<details>
<summary>No release yet, or want the newest unreleased version? Build the zip yourself.</summary>

Download the repository (**Code → Download ZIP** on GitHub) and unzip it. Then make a zip of the folder `skills/music-theory`. The zip must contain the folder `music-theory/` with `SKILL.md` inside it, and the folder name must stay `music-theory`. From a terminal:

```bash
cd skills && zip -r ../music-theory.zip music-theory
```
</details>

## 3. Upload it

1. Open [Customize → Skills](https://claude.ai/customize/skills).
2. Click **+**, then **+ Create skill**, then **Upload a skill**.
3. Choose `music-theory.zip`.
4. Make sure the switch next to **music-theory** is on.

## 4. Use it

Start a new chat and ask normally. Claude loads the skill on its own when the question is about music theory, analysis, or piano pedagogy. Some things to try:

- *"Show me a German augmented sixth resolving to V in C minor."*
- *"Quiz me on seventh-chord inversions, one question at a time."*
- *"Check my part-writing."* Attach a photo of your chorale, or type the notes (e.g. "S: E5 D5 C5, A: G4 G4 E4 …").
- *"Compare the reading approaches of Piano Adventures and The Music Tree."*

**What you'll see**
- Musical examples open in a panel next to the chat (an *artifact*), drawn on real staves.
- Press **▶ Play** to hear an example. (The sound is a simple built-in synthesizer, not a real piano.)
- A **red box** under a staff means the notation has an error. Tell Claude, and it will fix it.
- Under each staff, the notes are also written out in text, so you can check them or ask about a specific one.

**Tips**
- Tell Claude which textbook your course uses (e.g. Aldwell & Schachter, Kostka & Payne, Laitz). Labeling conventions differ between textbooks, and Claude will follow yours.
- For photos of scores: Claude transcribes the passage and asks you to confirm it before analyzing, because reading notes from a photo is error-prone.
- For ear training, ask Claude to hide the answer. It will draw the example without labels, and you press Play.

## Updating to a new version

Open [Customize → Skills](https://claude.ai/customize/skills), turn **music-theory** off, click **…** → **Delete**, and then upload the new zip as in step 3.

## If something doesn't work

| Problem | Fix |
|---|---|
| The upload is rejected | Check that the zip contains a `music-theory/` folder with `SKILL.md` in it, not the files on their own or a folder with a different name. |
| Claude doesn't seem to use the skill | Check that the skill's switch is on and code execution is enabled (step 1). Or ask directly: *"Use the music-theory skill to …"*. |
| The staff panel shows the ABC text instead of notes | The notation library couldn't load. Reload the page. If it keeps happening, ask Claude for the ABC text and paste it into any ABC viewer. |
| No sound | Click **▶ Play** again (browsers only allow sound after you click), and check that your device isn't muted. |

Help Center reference: [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).
