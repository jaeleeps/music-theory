# Privacy Policy

_Last updated: 2026-10-05_

**music-theory** is a skill and plugin made of Markdown instructions (`SKILL.md`), reference files (`references/`), an HTML page template (`assets/score.html`), and two helper scripts (`scripts/read_musicxml.py`, `scripts/zoom.py`). It has no hooks or MCP servers.

- **No data collection.** The skill does not collect, store, or transmit any data. It has no telemetry or analytics.
- **One network request, in pages you open.** When your agent builds a score page from the template and you open it, the page loads the open-source [abcjs](https://github.com/paulrosen/abcjs) library from `cdnjs.cloudflare.com` to draw the notation. Nothing you type is sent anywhere by the page. Playback is synthesized in your browser.
- **The scripts stay local.** They run only on a file you provide: `scripts/read_musicxml.py` reads a MusicXML file and prints its notes as text (Python standard library only), and `scripts/zoom.py` saves enlarged crops of a score image (Pillow). Neither makes network requests. In claude.ai they run in Claude's code-execution sandbox.
- **Your conversation stays with your agent.** Whatever you share (questions, homework, score images) is handled by your AI agent under its provider's privacy policy, not by this skill.

Questions: open an issue at https://github.com/jaeleeps/music-theory/issues.
