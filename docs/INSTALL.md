# Install Guide

Full instructions for every supported platform. Pick yours.

---

## Claude — web / desktop / mobile (claude.ai)

1. Download this repository as a `.zip` (or clone it and re-zip the folder —
   the zip's top-level folder name must match `name:` in `SKILL.md`).
2. In Claude: **Settings → Capabilities → Skills → Upload skill**.
3. Upload the `.zip`.

## Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r entrepreneur-business-intelligence-cfo ~/.claude/skills/
```

Project-scoped instead of user-scoped: put it in `.claude/skills/` inside your
repo.

## Claude Agent SDK / Anthropic API

Point your skills directory at the parent folder containing this repo, or
paste the contents of `platforms/system-prompt.txt` into the `system`
parameter of your API calls.

## OpenAI — Custom GPT

1. Create a GPT → **Configure** → **Instructions**.
2. Paste the full contents of `platforms/universal-compact-core.md`
   (7,873 characters — fits under the 8,000-char cap; re-check the count after any edit).
3. Optional: enable **Knowledge** and upload the `references/*.md` files and
   `assets/business-data-intake-template.csv`.
4. Optional: enable **Code Interpreter** and upload `scripts/cfo_calc.py` so
   the GPT can run it directly.

## OpenAI — Assistants API / raw API calls

Use `platforms/system-prompt.txt` as your system message.

## Google Gemini — Gems

1. Create a Gem.
2. Paste `platforms/gemini-gem-instructions.md` into the instructions field.
3. Attach the `references/` files as knowledge if your tier supports it.

## Google AI Studio / Vertex AI

Paste `platforms/system-prompt.txt` into **System Instructions**.

## Cursor

```bash
mkdir -p .cursor/rules
cp platforms/cursor-rule.mdc .cursor/rules/cfo-business-intelligence.mdc
```

## Windsurf

Copy `platforms/windsurf-rules.md` into a `.windsurfrules` file at your
project root, or add it via **Windsurf → Settings → Rules**.

## GitHub Copilot

```bash
mkdir -p .github
cp platforms/copilot-instructions.md .github/copilot-instructions.md
```

## Codex / Jules / Amp / Zed / any AGENTS.md-aware agent

```bash
cp platforms/AGENTS.md ./AGENTS.md
```

## Ollama / LM Studio / llama.cpp / self-hosted models

Paste `platforms/system-prompt.txt` as the system prompt. For models under
~8B parameters, the compact core is the right size for reliable adherence —
don't feed them the full reference set at once.

## Perplexity, Poe, Grok, DeepSeek, Mistral, Qwen, or any other chat UI

Paste `platforms/universal-compact-core.md` as your first message, or into
whatever custom-instructions field is available.

---

## Using the calculator directly

Standard library only. Python 3.8+. No `pip install` needed.

```bash
python3 scripts/cfo_calc.py list

python3 scripts/cfo_calc.py margins --revenue 920000 --returns 70000 \
    --cogs 467500 --variable 123250 --adspend 240000 --opex 180000

# one command for the whole picture, from a filled intake sheet
python3 scripts/cfo_calc.py intake --file assets/business-data-intake-example.csv

python3 scripts/cfo_calc.py roas --revenue 850000 --spend 240000 --cm-ratio 0.335

python3 scripts/cfo_calc.py price-test --price 1200 --varcost 720 \
    --units 1000 --increase 0.10

python3 scripts/cfo_calc.py npv --rate 0.15 --initial 500000 \
    --flows 150000,200000,250000,300000

python3 scripts/cfo_calc.py runway --cash 1200000 --burn 160750
```

Commands: `margins · unit · cac · roas · runway · ccc · npv · loan · dilution
· price-test · cashflow · inventory · intake`. Output is JSON.

**Cost buckets matter.** `--cogs` is landed product cost; `--variable` is the
per-order bucket founders forget (outbound shipping, payment gateway,
marketplace commission, RTO); `--adspend` is advertising; `--opex` is fixed
overhead EXCLUDING depreciation, which belongs in `--depreciation`. Each cost
goes in exactly one flag. Omit `--variable` or `--adspend` and `margins` warns
you, because leaving them out turns a loss into an apparent profit. The full
classification is in `references/01-formula-library.md`.

## Using the Excel dashboard

Open `assets/cfo-premium-dashboard.xlsx` directly — no setup required. Fill
the yellow cells on **1. Setup**, everything else recalculates.

To rebuild it after modifying `scripts/build_dashboard.py`:

```bash
# the workbook is a signed asset, so overwriting is opt-in
python3 scripts/build_dashboard.py --force
python3 scripts/verify_signature.py --generate   # re-sign afterwards

# or build elsewhere and leave the signed copy untouched
python3 scripts/build_dashboard.py -o /tmp/rebuild.xlsx
CFO_WORKBOOK=/tmp/rebuild.xlsx python3 scripts/test_workbook_excel.py
```

Requires `openpyxl==3.1.5` (see `requirements.txt`). The pin matters: the build
is deterministic, so a rebuild reproduces the committed workbook byte for byte,
and a different openpyxl changes the hash. Always open a rebuild in Excel, or
run the workbook tests against it, before shipping it.

## Verifying integrity

```bash
python3 scripts/verify_signature.py
```

Confirms every file matches its published SHA-256 hash and still carries the
author attribution. Exits non-zero if anything was modified or stripped.

---

*Entrepreneur Business Intelligence & CFO — **Md Kamrul Hasan** ·
https://github.com/Kamrul5242 · signature `MKH-EBIC-2.2.3`*
