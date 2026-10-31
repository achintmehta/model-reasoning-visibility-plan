# probe-prompts: the prompt each arm actually renders, per model

"Does a coding agent's model need to re-read its own reasoning?" compares arms
that differ only in what the model is shown of its own earlier reasoning:

| arm    | thinking | past reasoning sent back |
|--------|----------|--------------------------|
| OFF    | off      | nothing to send          |
| UNSEEN | on       | no                       |
| SEEN   | on       | yes (`reasoning_content`)|

Sending the reasoning back is not the same as the model seeing it. The server that hosts the models (llama-server)
runs every request through the model's own chat template, and a template can drop a past turn's reasoning: some have
no slot for it, some read a field of another name, some keep it only after the last user message. If that happens, SEEN
and UNSEEN prompts come out identical and the treatment is null, while our agent's run manifest still records that the reasoning was
sent. These files are the evidence that, for each model, the treatment actually reaches the prompt (protocol section 4.2,
"the prompt probe").

To check this, we use llama-server's `/apply-template` endpoint. It takes the same request body
as a chat request, applies llama.cpp's pre-processing and the model's chat template, and returns
the finished prompt without generating anything. Inspecting that prompt shows whether the past
reasoning is in the text the model is given.

## The canonical exchange

Every model and arm renders the same short agentic exchange: a system message, a user task,
and two earlier assistant turns, each with a tool call, a tool result, a line of visible
prose and (in SEEN only) a line of reasoning. The strings are short stand-ins, not the study's
real system prompt and task: what the probe tests is where each template puts each part, and
a short exchange makes every part easy to find in the rendered prompt. They are set in
`template_probe.py` of the harness repository (frozen tag
`model-reasoning-visibility-plan-freeze-101926`).

The fixed strings, with the labels the checks below use:

| label | role and field | string |
|-------|----------------|--------|
| system | system message | `You are a software engineer. [SYSTEM]` |
| task | user message | `Build a message board. [TASK]` |
| C1 | first assistant turn, visible text (`content`) | `Starting with the manifest.` |
| R1 | first assistant turn, reasoning (`reasoning_content`, SEEN only) | `The task needs a package.json before anything else, so write that first.` |
| call 1 | first assistant turn, tool call `c1` | `write_file` with arguments `{"path": "package.json"}` |
| result 1 | tool message answering `c1` | `wrote package.json` |
| C2 | second assistant turn, visible text | `Now the server.` |
| R2 | second assistant turn, reasoning (SEEN only) | `The server file comes next; it has to import express and listen on 3000.` |
| call 2 | second assistant turn, tool call `c2` | `write_file` with arguments `{"path": "server.js"}` |
| result 2 | tool message answering `c2` | `wrote server.js` |
| nudge | a user message appended for one extra SEEN render only | `You did not call any tool. If the task is complete, call finish.` |

`[SYSTEM]` and `[TASK]` are literal markers that make the two messages easy to find. The nudge's
wording differs from the harness's own finish nudge (protocol section 4.4) on purpose: only
its role matters here, because several templates hide reasoning that sits before the last
user message, and the nudge moves that boundary.

The SEEN request, exactly as sent to `/apply-template` (UNSEEN and OFF are the same without the
two `reasoning_content` fields, and the nudged render adds the nudge as a last `user` message):

```json
{
  "messages": [
    {"role": "system", "content": "You are a software engineer. [SYSTEM]"},
    {"role": "user", "content": "Build a message board. [TASK]"},
    {"role": "assistant", "content": "Starting with the manifest.",
     "reasoning_content": "The task needs a package.json before anything else, so write that first.",
     "tool_calls": [{"id": "c1", "type": "function",
                     "function": {"name": "write_file", "arguments": "{\"path\": \"package.json\"}"}}]},
    {"role": "tool", "tool_call_id": "c1", "content": "wrote package.json"},
    {"role": "assistant", "content": "Now the server.",
     "reasoning_content": "The server file comes next; it has to import express and listen on 3000.",
     "tool_calls": [{"id": "c2", "type": "function",
                     "function": {"name": "write_file", "arguments": "{\"path\": \"server.js\"}"}}]},
    {"role": "tool", "tool_call_id": "c2", "content": "wrote server.js"}
  ],
  "tools": [{"type": "function", "function": {
    "name": "write_file", "description": "write a file",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}}],
  "chat_template_kwargs": { "...": "the arm's own switches, below" }
}
```

The `chat_template_kwargs` of each arm are taken from the run wrapper's own `think_body()`, so
the probe sends the same switches a study run sends (protocol section 4.1):

| model | OFF | UNSEEN and SEEN |
|-------|-----|-----------------|
| Gemma-4-31B-it, Gemma-4-26B-A4B-it | `{"enable_thinking": false, "preserve_thinking": true}` | `{"enable_thinking": true, "preserve_thinking": true}` |
| Qwen3.6-27B, Qwen3.6-35B-A3B | `{"enable_thinking": false, "preserve_thinking": true}` | `{"enable_thinking": true, "preserve_thinking": true}` |
| Seed-OSS-36B-Instruct | `{"thinking_budget": 0}` | no field |
| gpt-oss-20b | (no OFF arm) | `{"reasoning_effort": "medium"}` |
| GLM-4.7-Flash | `{"enable_thinking": false, "clear_thinking": false}` | `{"enable_thinking": true, "clear_thinking": false}` |
| Muse Glimmer 30B | (no OFF arm) | `{"reasoning_strength": "high"}` |

Every study model replays reasoning in the `reasoning_content` field (`replay_format=field`).
The probe also has an `inline-think` route, which writes the reasoning into the visible text as
`[THINK]...[/THINK]` and sends no field. It was used only for Magistral, a model later retired
(protocol Appendix A), as was the system-prompt preamble the probe appends for Magistral alone.

## What is in this folder

The folder holds probes for eleven models, more than the study finally uses. Eight are the
study's models, the ones the regenerate command below lists: `gemma-q4`, `gemma-moe-q4`,
`qwen-q4`, `qwen-moe-q4`, `seed-q4`, `gptoss-20b`, `glm-q4` and `muse-q4xl`. The other three,
`granite-q4` (Granite 4.2-30B), `magistral-q4xl` (Magistral-Small-2509) and `nemotron-q4`
(Nemotron-3-Nano-30B-A3B), were candidates that passed the probe and were later retired on
their smoke runs (protocol Appendix A, requirement 4). Their files are kept as the record behind
those decisions and play no part in the analysis.

For each model key (the run wrapper's names), the folder has:

| file | contents |
|------|----------|
| `<model>.OFF.txt`    | the prompt the server rendered for the OFF arm (absent for a model with no off-switch: gpt-oss, Muse Glimmer) |
| `<model>.UNSEEN.txt` | the prompt rendered for UNSEEN: thinking on, no past reasoning sent |
| `<model>.SEEN.txt`   | the prompt rendered for SEEN: thinking on, both past turns' reasoning sent |
| `<model>.server.log` | the llama-server log of the probe session (boot, model load, the probe's requests) |

Each `.txt` file is the exact string `/apply-template` returned: llama.cpp's own
pre-processing followed by the GGUF's embedded Jinja template, i.e. the text the model would
be given before generating.

## How to read them

- SEEN must contain both R1 and R2. UNSEEN and OFF must contain neither.
- The assistant's own prose (C1, C2) must survive in every arm: a template that keeps the
  reasoning but drops the prose is a different defect. Two study models are exceptions, because
  of how their templates work rather than a defect. gpt-oss-20b's SEEN prompt carries the
  reasoning in place of the prose, so C1 and C2 are absent from it. Muse Glimmer's template
  renders no prose on a turn that has a tool call, so C1 and C2 are absent from both its arms.
- The probe also renders SEEN with the stand-in nudge (above) appended as a last user message,
  because several templates hide reasoning that sits before the last user message. The
  console output reports whether both turns stay visible.

The quickest check is a diff between arms:

    diff <model>.UNSEEN.txt <model>.SEEN.txt

The added characters are the treatment. The per-model figures are in the protocol's section 4.2
table (template sha256, characters added, verdict).

## How to regenerate

From the `eval-coding-agent` repository, in WSL, with no other llama-server running:

    ./template_probe.sh gemma-q4 qwen-q4 seed-q4 gptoss-20b glm-q4 qwen-moe-q4 gemma-moe-q4 muse-q4xl

For each model the script:

1. resolves the GGUF through the run wrapper's model map (`run_one_with_server.sh`),
2. boots the pinned llama.cpp build (b10964) on it with `--jinja`,
3. calls `/apply-template` once per arm via `template_probe.py`, prints a verdict line per
   arm (prompt length, whether R1 and R2 are present), and writes the files above,
4. stops the server before moving to the next model.

Environment variables: `SERVER_EXE` (path to `llama-server.exe`), `MODELS_ROOT`, `PORT`
(default 7777), `SERVER_HOST`, `OUT_DIR` (default `probe-prompts/` next to the script).

Notes:
- The probe's server omits two of the study's frozen serving flags, `--swa-full` and
  `-lv 5`. Neither affects template rendering: the first changes how the attention cache is
  kept, the second only how much the server logs.
- Rendering is deterministic: the same GGUF (checked by its sha256 in
  `quant-registry.json`) and the same engine build give byte-identical files. A difference
  means the template, the engine or the request body changed.
- Nothing here is generated by the model. `/apply-template` renders a prompt without running
  inference, so the probe takes seconds per model and needs no sampling settings.
