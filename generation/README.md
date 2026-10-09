# How the designs were generated

The code that generated the benchmark designs is not included; this folder records what every model
was sent (paper, Appendix "Evaluation dataset", "Generation").

| File | Contents |
|---|---|
| `system_prompt.txt` | The system prompt |
| `user_prompt_template.txt` | The user message: the same wrapper for every prompt, with the prompt text in place of `{task}` |
| `tools.json` | The tool the design is submitted through (`submit_html`), and the one offered only to finish a truncated document (`continue_html`) |
| `follow_up_messages.json` | The messages sent back when a submission was truncated, when an inline script did not parse, or when the page threw while loading |
| `document_shape_note.txt` | An optional paragraph inserted before `<task>`, asking for the full document from `<!DOCTYPE html>` to `</html>` |
| `config.json` | Sampling, the follow-up rounds, and each model's identifier, reasoning effort and output-token limit |

Each prompt in `data/prompts/` goes to the model as one user turn, and the turn must end with a
`submit_html` call carrying the complete document. Temperature and sampling are the providers'
defaults; the reasoning effort per model is in `config.json` (the paper's Table 1).

A submission is then checked, in order:

1. **Complete.** A document cut off at the output-token limit is not kept. The conversation
   continues, at low effort, with `continue_html`: the model echoes the last line it sent and
   supplies the rest, and the two are joined only if the echoed line matches.
2. **Parses.** Every inline script is parsed. If one fails, the parser's message goes back with
   a request to resubmit the whole document with only that error fixed.
3. **Runs.** The page is loaded in a browser. If it throws while loading, the error and the
   offending source lines go back with the same request.

Steps 2 and 3 run at low effort, for at most the number of rounds given in `config.json`.
