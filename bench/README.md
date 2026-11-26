# Coding assistant tests: Pi and opencode, three local models

**English** | [Türkçe](README.tr.md)

A record of how three models running in Ollama on the server handled the same three tasks in two coding assistants (harnesses) on a Windows PC.
The user ran the tests by hand. Results were judged by `git diff` and the check scripts below, not by what the model claimed.

- Dates: Pi 2026-11-25, opencode 2026-11-26. Commands and details (Turkish): [LOG.md](../LOG.md).
- In this folder: [prompts](prompts/), [starting files](tests/), [check scripts](checks/).

## Models and harnesses

| Model (Ollama) | Context | Output limit | Note |
|---|---|---|---|
| `gemma4:e4b` | 64K | 8192 | Small, fast |
| `inkling-pi:32k` | 32K | 8192 (opencode test 3 runs 2-3: 4096) | Derived from `inkling-2-mini:26b-a5b-iq4_NL`, `num_ctx 32768`, `num_batch 128` |
| `bonsai-pi:64k` | 64K | 16384 | Ternary Bonsai 2.5 27B `Q2_0`, sampling settings from the model card |

| | Pi | opencode |
|---|---|---|
| Version | `1.6.0` (`@earendil-works/pi-coding-agent`) | `2.4.2` (updated itself from `1.19.6` on first launch) |
| Connection | `openai-completions`, `http://<server>:11434/v1` | `@ai-sdk/openai-compatible`, same address |
| Thinking | `--thinking medium` | `reasoningEffort: "medium"` in the model settings (verified that `reasoning_effort` is sent) |
| Command approval / sandbox | None | Does not ask with default settings, no sandbox |
| Compaction | `reserveTokens 10000`, `keepRecentTokens 8000` | Default: at least 16K kept free, 15K tokens kept afterwards. Set to `buffer 6144`, `keep.tokens 4000` for Inkling |

## Tests

Each run used its own git repo, started from a clean state tagged `baseline`, in a new session.

| # | Task | What it measures | Files | Prompt |
|---|---|---|---|---|
| 1 | One-line bug (`len(xs) + 1`) | Simple read, edit, run the test | [tests/test1](tests/test1) | [prompts/test1.txt](prompts/test1.txt) |
| 2 | Two bugs in two files (cents are dropped, the discount is subtracted as an amount instead of a percentage) | Finding the cause in a different file from the symptom, leaving the test alone | [tests/test2](tests/test2) | [prompts/test2.txt](prompts/test2.txt) |
| 3 | New feature from a spec: `parse_duration` / `format_duration` plus its own tests | Following every rule, writing tests, not claiming false success | [tests/test3](tests/test3) | [prompts/test3.txt](prompts/test3.txt) |

Tests 1 and 2 ran once per model, test 3 three times.

**Rules:** the user may only type `Continue.` (at most 3 times), and a run is stopped after 10 minutes. The checks were kept in a folder the model could not see.

### Checks

> **Warning:** the check scripts run the model's code on your machine, without a sandbox. Read the code first.

| Script | What it does |
|---|---|
| [checks/check.py](checks/check.py) `<folder> <1\|2\|3>` | Did the changed files stay within the allowed ones (`SCOPE`)? Tests 1-2: runs the **original** test file from `baseline`, so an edited test cannot pass. Test 3: runs the hidden check below and the strict test rule. |
| [checks/hidden_check.py](checks/hidden_check.py) `<folder>` | 243 behavior checks (valid and invalid inputs plus 205 round trips). Runs the model's tests against a correct implementation and 8 deliberately broken ones (mutants). |
| [checks/strict_strength.py](checks/strict_strength.py) `<folder>` | Mutant score with a strict rule: exit code 0, no line mentions `FAIL`, last line is exactly `PASS`. (The loose rule is fooled by scripts that print `PASS: ...`.) |
| [checks/ascii_check.py](checks/ascii_check.py) `<folder>` | The "ASCII digits" rule: inputs such as `"٥s"` and `"５m"` must raise `ValueError`. Not in the hidden check; added later. |

Most of the 243 checks are round trips, so the percentage is misleading; the inputs that were missed are what matter.

### Running it yourself

```powershell
# a separate folder for each run
$ws = "C:\bench\gemma\test3"
New-Item -ItemType Directory -Force $ws | Out-Null
Copy-Item -Recurse bench\tests\test3\* $ws; Copy-Item bench\tests\test3\.gitignore $ws
cd $ws; git init -q; git add -A; git commit -qm baseline; git tag baseline
# open the harness in this folder, paste the content of prompts\test3.txt; when it is done:
git diff baseline; git status --short
python <repo>\bench\checks\check.py . 3
python <repo>\bench\checks\strict_strength.py .
python <repo>\bench\checks\ascii_check.py .
```

opencode settings (`~/.config/opencode/opencode.jsonc`, shortened):

```jsonc
{
  "compaction": { "buffer": 6144, "keep": { "tokens": 4000 } },
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://gpu-server:11434/v1", "apiKey": "ollama" },
      "models": {
        "inkling-pi:32k": {
          "reasoning": true, "tool_call": true,
          "limit": { "context": 32768, "output": 4096 },
          "options": { "reasoningEffort": "medium" }
        }
      }
    }
  }
}
```

opencode 2.x has no `-m` flag; the model is picked inside the TUI (`ctrl+p`). After changing the settings, run `opencode reload`.

## Results

Times: in Pi, approximate working time excluding waits; in opencode, from the first request to the last reply (from the opencode database).
Thinking: thousands of characters. In test 3, the three values are the three runs.

### Pi

| | gemma4:e4b | inkling-pi:32k | bonsai-pi:64k |
|---|---|---|---|
| Test 1 | Fixed it after one help message | Passed, 32 s | Passed, 20 s |
| Test 2 | Passed, 11 s | Passed, 26 s | Passed, 63 s |
| Test 3 hidden check (/243) | 238, 238, 238 | 243, 243, 243 | 243, 243, 243 |
| Test 3 ASCII rule | ✗ ✗ ✗ | ✗ ✓ ✓ | ✗ ✗ ✗ |
| Test 3 own tests (strict) | ✗ ✓ ✓ | ✓ ✓ ✓ | ✓ ✓ ✓ |
| Test 3 mutants (strict, /8) | not measurable, 8, 8 | 8, 8, 8 | 8, 8, 8 |
| Test 3 `Continue.` | 0, 1, 1 | 0, 0, 0 | 0, 0, 0 |
| Test 3 time (s) | 80, 91, 113 | 268, 233, 160 | 131, 142, 240 |
| Test 3 thinking | 18, 24, 31 | 6, 7, 2 | 3, 3, 8 |
| Lost tool calls (5 runs) | 3 | 0 | 0 |

### opencode

| | gemma4:e4b | inkling-pi:32k | bonsai-pi:64k |
|---|---|---|---|
| Test 1 | Passed, 20 s | Passed, 124 s (includes model load) | Passed, 40 s |
| Test 2 | Passed, 18 s | Passed, 156 s | Passed, 94 s |
| Test 3 hidden check (/243) | 243, 241, 238 | 243 (timeout), 243, 243 | 243, 243, 243 |
| Test 3 ASCII rule | ✗ ✗ ✗ | ✓ ✓ ✓ | ✓ ✗ ✓ |
| Test 3 own tests (strict) | ✗ ✓ ✗ | ✗ ✓ ✓ | ✓ ✓ ✓ |
| Test 3 mutants (strict, /8) | not measurable, 7, not measurable | not measurable, 8, 8 | 8, 8, 8 |
| Test 3 `Continue.` | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| Test 3 time (s) | 148, 91, 65 | stopped (~15 min), 506, 400 | 276, 524, 704 |
| Test 3 thinking | 24, 15, 8 | 25, 9, 10 | 16, 33, 53 |
| Test 3 compactions | 0, 0, 0 | 2, 0, 0 | 0, 0, 0 |
| Lost tool calls (5 runs) | 0 (3 bad calls, fixed by itself) | 0 (2 bad calls, fixed by itself) | 0 |

opencode notes:
- **Gemma test 3:** run 1's test treats a valid input (`"1d 1m"`) as an error and imports `pytest`; the model blamed the test and called the job done.
  Run 2 accepts `"5 m"` and `format_duration(True)`. Run 3 makes the same five mistakes as in Pi (accepts `-5m`, `1.5h`, `1h,5m`, `1h foo`, `1h5`).
  It also prints another line after `PASS`.
- **Inkling test 3, run 1:** with the default compaction setting, it compacted at ~16.7K tokens in the 32K window, twice. Each time it forgot the files and started thinking again. It went past 10 minutes without running its test once and was stopped.
  The `duration.py` it left was correct (243/243, ASCII passed); the test file had a wrong expected value.
  Lowering the output limit to 4096 alone did not help (it still compacted at ~16.6K; that run was counted as invalid). With `compaction.buffer 6144` and `keep.tokens 4000`, runs 2 and 3 finished fully clean without a single compaction.
- **Bonsai test 3:** each run thought for 4-5.5 minutes on its first step. Run 3 went over the 10-minute limit (the user did not stop it), but its result is one of the cleanest: it also rejects `"1ſ"`.
- Gemma and Bonsai (64K) used at most ~31K and ~20K tokens; they never came near compaction, so the new compaction setting does not affect their results.

### Model comparison

| Model | Short verdict |
|---|---|
| **inkling-pi:32k** | Follows the rules most strictly: all 5 valid test 3 runs across both harnesses scored 243/243, and it passed the ASCII rule in 4 of 5. Recommended for writing code. In opencode it needs the compaction setting. |
| **bonsai-pi:64k** | All six test 3 runs scored 243/243 and 8/8; weak on the ASCII rule (Pi 0/3, opencode 2/3). For work that needs long context. Very slow in opencode. |
| **gemma4:e4b** | The fastest, but none of its test 3 runs is fully correct; it accepts invalid input and claims success too easily. For supervised small fixes. |

### Harness comparison

| | Pi | opencode |
|---|---|---|
| Correctness | Same level | Same level |
| Gemma's tool calls | 3 calls lost in 5 runs (Ollama could not parse them); Pi stopped without showing an error | None lost; bad calls came back as tool errors and the model fixed them itself |
| Speed (Inkling, Bonsai) | Faster, less thinking | In test 3, Inkling ~2× and Bonsai 2-4× slower; Bonsai thought 5-11× as much |
| Small context (32K) | No problems | The default compaction setting blocks the work; needs tuning |
| System prompt | Not measured | ~22-23K characters, 10-12 tools (first request ~10.7K tokens) |
| Updates | Manual | Updated itself; the command line changed (`-m` was removed) |

**Limits:** each cell is one to three runs, so the sample is small. Context and output limits differ between models. In opencode, Inkling's test 3 setup (output 4096, compaction) differs from the one in Pi. Times were not measured the same way in both harnesses.
