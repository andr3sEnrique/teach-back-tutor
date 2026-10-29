# Lesson JSON format for `build_lesson.py`

Write one JSON file per chunk, then run:

```bash
python3 <skill-dir>/scripts/build_lesson.py lesson-01.json
```

It writes `lesson-01.html` next to the JSON (or use `-o path.html`). The page is self-contained: audio is embedded, so the single file can be opened, moved or shared. Expect about 1 MB per 2 to 3 minutes of audio.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Page title, in the learner's language. |
| `subtitle` | no | One line of instructions, e.g. "Click a sentence to jump to it." in the learner's language. |
| `tracks` | yes | One or more narrations. Each gets a tab when there are several. |
| `tracks[].id` | yes | Short id, e.g. `"es"`, `"fr"`. |
| `tracks[].label` | no | Tab text, e.g. `"Español + términos FR"`. |
| `tracks[].lang` | yes | Language code (`es`, `fr`, `en`, `pt-BR`...). Picks the voice. |
| `tracks[].voice` | no | Exact voice name to force one (macOS: `say -v '?'` lists them). |
| `tracks[].text` | yes | The narration. Paragraphs separated by a blank line (`\n\n`). Wrap key terms in `{braces}` to highlight them; the voice reads them normally. |
| `figures` | no | List of `{"caption": "...", "svg": "<svg>...</svg>"}` shown above the transcript. Use `currentColor` in the SVG so it works in dark mode. |
| `glossary` | no | List of `{"term": "...", "def": "..."}`. |
| `glossary_title` | no | Heading for the glossary, in the learner's language (default "Glossary"). |

## Writing for the ear

The text is read aloud, so write it to be heard:

- Short sentences; one idea per sentence. Sentences are split on `. ! ? :` and each becomes a clickable line.
- Spell out what a voice would stumble on: "for example" rather than "e.g.", numbers in words when they are short.
- Acronyms the voice should spell: write them with spaces or explain them on first use.
- End with the hand-over to the learner ("Now it's your turn: explain these ideas in your own words.").

## Example: two tracks, key terms in the exam language

```json
{
  "title": "Sesión 1 · Les fondamentaux",
  "subtitle": "Haz clic en una frase para saltar a ese momento. Los términos resaltados están en francés.",
  "glossary_title": "Glosario",
  "tracks": [
    {
      "id": "es",
      "label": "Español + términos FR",
      "lang": "es",
      "text": "Empecemos por cuatro palabras clave.\n\nUn {actif} es lo que tiene valor. Por ejemplo, el expediente de un paciente.\n\nUna {menace} es lo que puede dañar ese activo.\n\nAhora te toca a ti: explícame estas nociones con tus propias palabras."
    },
    {
      "id": "fr",
      "label": "Tout en français",
      "lang": "fr",
      "text": "Commençons par quatre mots clés.\n\nUn {actif} est ce qui a de la valeur. Par exemple, le dossier d'un patient.\n\nUne {menace} est ce qui peut nuire à cet actif.\n\nÀ vous : expliquez-moi ces notions avec vos propres mots."
    }
  ],
  "figures": [
    {
      "caption": "Una amenaza explota una vulnerabilidad sobre un activo",
      "svg": "<svg viewBox='0 0 420 80' xmlns='http://www.w3.org/2000/svg' font-family='system-ui' font-size='14' fill='none' stroke='currentColor'><rect x='5' y='20' width='110' height='40' rx='8'/><text x='60' y='45' text-anchor='middle' fill='currentColor' stroke='none'>menace</text><path d='M115 40h40'/><rect x='155' y='20' width='110' height='40' rx='8'/><text x='210' y='45' text-anchor='middle' fill='currentColor' stroke='none'>vulnérabilité</text><path d='M265 40h40'/><rect x='305' y='20' width='110' height='40' rx='8'/><text x='360' y='45' text-anchor='middle' fill='currentColor' stroke='none'>actif</text></svg>"
    }
  ],
  "glossary": [
    {"term": "actif", "def": "Activo: lo que tiene valor y hay que proteger."},
    {"term": "menace", "def": "Amenaza: lo que puede causar daño."}
  ]
}
```

For a single-language lesson, use one track and leave out the labels.
