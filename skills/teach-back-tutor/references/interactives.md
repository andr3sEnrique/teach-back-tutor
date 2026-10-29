# Interactives: let the learner see the concept move

An interactive is a small live model of the idea. The learner changes something and watches what happens, so the distinction you are teaching becomes visible. It is not a quiz: nothing is scored and there is no right or wrong. It is for seeing.

The example that inspired this: a risk matrix with two sliders (likelihood, severity) and buttons for real cases from the learner's case study. Pressing "after changing the password" moves the dot down the likelihood axis while severity stays critical. That one move shows what a paragraph struggles to say: a security measure lowers likelihood, not impact, and what is left is the residual risk. See `assets/examples/risk-matrix.html`.

## What makes a good one

- **One distinction per interactive.** Decide the single thing the learner should be able to tell apart ("likelihood vs severity", "integrity vs confidentiality", "backup vs replication"). The control they move is the variable of that idea.
- **Presets from their own material.** Add 2 to 4 buttons with real cases from the learner's sources (their case study, their job, the exam's typical scenarios). Each preset sets the controls and shows a short note explaining what changed and, just as important, what did not.
- **Include the trap.** One preset should be the case where intuition fails (the measure that does not reduce impact, the incident that looks like a confidentiality breach but is an integrity one).
- **Cause and effect in the same view.** Controls and result side by side, updating instantly. No "submit" button.
- **Words where the learner needs them.** Labels in the learner's language, key terms in the exam language when that applies (same convention as the narration).
- **Small.** One screen, works at phone width (320 px). A few dozen lines of JS, not an app.

## Patterns

Pick the one that matches the concept:

| Pattern | Use when | Example |
|---|---|---|
| **Model with sliders** | an output depends on inputs | risk = likelihood × severity; a threshold; a formula; capacity vs load |
| **Before / after toggle** | a change or a measure has an effect | apply MFA: which attack paths close, which stay open |
| **Scenario lights up categories** | a case must be classified | pick an incident, see which of D, I, C, T light up, with one line each on why |
| **Step through a process** | there is an order or a lifecycle | attack chain, PDCA cycle, incident response, a protocol handshake: Next/Back, active step highlighted, the note says what happens and who acts |
| **Side-by-side contrast** | two concepts get confused | backup vs replication: toggle "ransomware encrypts the data" and watch one copy survive and the other get encrypted |
| **Clickable diagram** | the parts of a whole matter | click each box of an architecture for what it does; a "tell me more" link per part |

Combine at most two patterns in one interactive. If a chunk has two distinctions, build two small interactives rather than one big one.

## Technical contract (for `build_lesson.py`)

An interactive is an HTML fragment (no `<html>`, `<head>` or `<body>`) placed inside a card on the lesson page. Write it to its own file, e.g. `lesson-01-matrix.html`, and reference it from the lesson JSON:

```json
"interactives": [
  {"title": "Vraisemblance × gravité", "hint": "Move the sliders or press a case.", "file": "lesson-01-matrix.html"}
]
```

(`"html": "..."` inline also works, but a separate file avoids escaping.)

Rules, so several interactives and the page itself don't break each other:

- **Scope everything to your card.** Start the script with `const R = document.currentScript.parentElement;` and find elements with `R.querySelector(...)`. Use `data-k="..."` attributes instead of `id`s. Wrap the script in `(() => { ... })();`.
- **Prefix your CSS classes** with a short tag (`rm-`, `dict-`, ...). Don't style bare tags like `button` or `div`; the page already styles buttons.
- **Use the page's colours** so light and dark mode both work: `--tx` text, `--mut` secondary text, `--bg` page, `--card` card, `--bd` borders, `--ac` accent, `--hl`/`--hlt` highlight background/text, `--mk`/`--mkt` key-term background/text, and for levels `--okbg`/`--ok`, `--warnbg`/`--warn`, `--badbg`/`--bad`, `--crit`/`--oncrit`. In SVG, use `currentColor` or these variables.
- **No external scripts, fonts or network calls.** The page must work offline and when opened as a file.
- **"Tell me more" links**: call `sendPrompt('Explain X again with another example')` on a clickable part. In a chat widget the host sends it to the tutor; on the standalone page it is copied so the learner can paste it into the chat. Set `"copied_text"` in the lesson JSON to translate the confirmation ("Copiado, pégalo en el chat:").

## Without the lesson script

The same fragment works elsewhere:

- **Inline chat widget** (an environment with a tool that renders HTML/SVG widgets in the conversation): show it there, so the learner plays with it right next to your explanation. `sendPrompt` is native there.
- **Artifact or canvas**: wrap it in a minimal page with the colour variables defined on `:root`.
- **No rendering at all**: describe the presets as a small table ("case → likelihood, severity, level, why"). Weaker, but the contrast is still the point.
