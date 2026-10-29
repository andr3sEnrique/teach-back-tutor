# teach-back-tutor

A skill for Claude Code, Claude.ai and other agents that read `SKILL.md` (Codex, Cursor, etc.). It turns the agent into a teacher who runs real study sessions:

1. **Teach**: explains a chunk of the topic, with a narrated audio lesson (synced transcript, highlighted key terms, glossary), diagrams and concrete examples.
2. **Teach back**: you explain it in your own words and answer 2 or 3 questions (restate, apply, trap).
3. **Feedback**: it asks Socratic questions so you find your own mistakes first, then corrects what is still wrong and says why.

It works in any language: it answers in the language you write in. If you study in one language for an exam in another, it keeps the key terms in the exam language, with a glossary. It can keep a `study-progress.md` file so the next session starts by reviewing your weak points.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills) (Claude Code, Codex, Cursor and others):

```bash
npx skills add andr3sEnrique/teach-back-tutor
```

As a Claude Code plugin:

```text
/plugin marketplace add andr3sEnrique/teach-back-tutor
/plugin install teach-back-tutor@teach-back-tutor
```

Manually: copy `skills/teach-back-tutor/` into `~/.claude/skills/` (or your agent's skills folder).

On Claude.ai: download `skills/teach-back-tutor` as a zip and upload it in Settings → Capabilities → Skills.

## Use

Just ask to study something, in your own words:

> I have an oral exam on network security in two weeks, here are my slides. Teach me the way a teacher would: explain first, then I explain back and you correct me.

> Repasemos el tema 3 de mis apuntes, explícame primero y luego te lo explico yo.

## Audio lessons

`scripts/build_lesson.py` builds one self-contained HTML page per lesson, with the audio embedded. It needs Python 3 and a system voice: `say` on macOS (built in) or `espeak-ng` on Linux. Without a voice it builds a transcript-only page and the method works the same. See `skills/teach-back-tutor/references/lesson-format.md`.

### Choosing the voice

By default it uses the best voice installed for the language (Premium > Enhanced > standard). To pick another one, just tell the tutor ("use another voice", "list the voices"): it shows the installed voices and remembers your choice. Or set it yourself:

```bash
python3 skills/teach-back-tutor/scripts/build_lesson.py --list-voices es
export TEACH_BACK_VOICE="es=Paulina,fr=Thomas"   # lasting default
```

On macOS, nicer voices can be downloaded in System Settings > Accessibility > Spoken Content > System voice > Manage Voices.

## License

MIT

---

**ES:** Skill de "profesor": primero explica (audio, diagramas, ejemplos), luego tú le explicas lo que entendiste y respondes preguntas, y al final te hace preguntas para que encuentres tus propios errores antes de corregirte. Responde en el idioma en que le escribas.
