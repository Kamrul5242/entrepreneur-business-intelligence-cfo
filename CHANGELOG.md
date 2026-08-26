# Changelog

## Unreleased

### Fixed — `scripts/cfo_calc.py`
- **Every command crashed on Python 3.13+.** A bare `%` in the `dilution` help
  string made argparse raise `ValueError: badly formed help string` while
  building the parser, before any argument was read. On 3.8–3.12 the same
  string broke `--help`. Escaped to `%%`.
- `runway` graded a cash-generating business as `CRITICAL — survival mode`.
  A negative burn divided into cash produced a negative runway that fell
  through the `< 3` test. Non-positive burn is now reported as
  `CASH POSITIVE` / `NO NET BURN` with no month count.
- `unit --target-profit` raised `TypeError: type NoneType doesn't define
  __round__` when contribution margin was zero — the exact case the command
  has an ALERT for. Break-even units, break-even revenue and break-even ROAS
  now return `null` instead of negative values when CM ≤ 0.
- `roas` called an exact break-even `LOSING MONEY`; it now reports
  `BREAK-EVEN on ads`.
- `loan --monthly-ocf` raised `TypeError` comparing a `None` DSCR when EMI
  was zero.
- `--annual-rate` now documents that it takes a decimal (`0.14`), matching
  `npv --rate`.

### Fixed — `scripts/build_dashboard.py`
- The script took no arguments, so `--help` silently rebuilt and overwrote
  `assets/cfo-premium-dashboard.xlsx` — a signed asset — making
  `verify_signature.py` report `TAMPERED`. It now parses `--output/-o` and
  `--force`, and refuses to overwrite an existing workbook without `--force`.
- Note on reproducibility: a rebuild is not byte-identical to the published
  workbook. The embedded document-properties signature survives, but openpyxl
  version differences change the archive layout, so the SHA-256 changes.
  Re-run `verify_signature.py --generate` after any rebuild.

### Fixed — docs
- `SIGNATURE.json` regenerated; it now also covers `.gitattributes`,
  `CITATION.cff` and `llms.txt`, which previously reported as unmanifested.
- README: corrected the compact-core character count (7,523, not 7,529),
  added the three files missing from the repo tree, documented that
  `universal-compact-core.md`, `system-prompt.txt` and
  `gemini-gem-instructions.md` are byte-identical, and updated the rebuild
  command for the new `--force` guard.
- Added `.gitattributes` (`* -text`). Git for Windows defaults to
  `core.autocrlf=true`, which rewrote LF to CRLF on clone and made all 24
  signed text files fail verification with a false `TAMPERED`.

## 2.1.0 — 2026-08-20

### Removed
- All marketplace/store links. GitHub is now the sole distribution reference.

### Added — multi-currency
- `references/08-currency.md` — 34 currencies, **BDT default**, with detection
  priority, South Asian lakh/crore grouping (2-2-3 digit blocks), zero-decimal
  (JPY/KRW/IDR/VND) and three-decimal (KWD/BHD/OMR) handling, FX exposure
  analysis, and the break-even exchange rate formula for exporters.

### Added — premium Excel dashboard
- `assets/cfo-premium-dashboard.xlsx` — 5 sheets, 90 live formulas, zero
  hardcoded results, recalculation-verified error-free.
- Currency dropdown drives symbol and name resolution workbook-wide.
- KPI cards with conditional RED/GREEN status, unit economics block,
  cash & runway, liquidity & cash-cycle panel, break-even, automatic verdict
  string, and a profit chart.
- Scenario sheet with editable drivers and a price-sensitivity table.
- Navy/slate/gold palette, Arial, frozen panes, data validation, cell comments.
- `scripts/build_dashboard.py` rebuilds it reproducibly.

### Added — digital signature
- Signature ID `MKH-EBIC-2.1.0` embedded in 9 independent locations.
- `SIGNATURE.json` — SHA-256 manifest of all 24 files.
- `scripts/verify_signature.py` — detects modified, missing, or
  attribution-stripped files; exit code 1 on tamper.
- XLSX signature sheet is locked and password-protected; signature also written
  to workbook document properties.

### Changed — token efficiency
- `SKILL.md` reduced from ~9,400 to ~6,400 characters, now a pure router with an
  explicit token-budget policy: output length scales to question size, at most 3
  reference files per turn, no restating the user's numbers, arithmetic past two
  steps offloaded to the calculator.
- Net effect vs v1.0: **~75% fewer tokens loaded per trigger.**

## 2.0.0 — 2026-08-20

Full rebuild by Md Kamrul Hasan.

### Corrected — real errors in v1.0

- **Liquidity section added.** v1.0's health scorecard graded "Liquidity" but no
  liquidity ratio existed anywhere in the file. Added current ratio, quick
  ratio, cash ratio.
- **Solvency formulas added.** v1.0 listed debt-to-equity and debt service as
  things to "track" without ever defining them. Added D/E, debt-to-assets,
  net debt/EBITDA, equity ratio, DSCR.
- **Investment appraisal added.** v1.0 named DCF in the valuation section and
  promised "evaluates an investment" in its description, but contained no NPV,
  IRR, payback, or discount-rate method. All added, plus WACC.
- **LTV formula disambiguated.** `Avg Revenue per Customer × Gross Margin ×
  Lifetime` double-counts when "revenue per customer" already means lifetime
  revenue. Rewritten as `ARPU_period × Gross Margin (decimal) × Lifetime (same
  period unit)`, with churn-derived and repeat-purchase variants and explicit
  validity conditions.
- **Margin denominators standardized.** v1.0 used `Revenue` for gross margin but
  `Net Revenue` for net margin, and defined neither. All margins now use net
  revenue, with the term defined.
- **EBITDA condition stated.** `EBITDA = Operating Profit + D&A` is only true
  when D&A sits inside operating expenses. Now stated, with the alternative
  build-up from net profit.
- **Contribution margin separated from gross margin** throughout, since the two
  were used loosely in v1.0 and they drive different decisions.

### Added

- Break-even ROAS (`1 / CM ratio`) — the number that actually decides ad scaling
- MER alongside ROAS, to catch platform over-attribution
- Paid vs blended vs fully-loaded CAC, as three distinct metrics
- Break-even volume loss formula for price changes
- Cash break-even, margin of safety, degree of operating leverage
- GRR vs NRR, SaaS quick ratio, Rule of 40
- Landed cost, RTO/COD provision, dead stock, GMROI, sell-through
- Pre-order economics and negative cash conversion cycle
- Marketplace vs own-store contribution comparison
- SAFE/convertible note conversion and option-pool-shuffle warning
- EMI, effective annual rate, DSCR against operating cash flow
- Customer and supplier concentration thresholds
- Eight named diagnosis patterns (v1.0 had six, none prioritized)
- Root-cause decision trees for the three most common founder questions
- `scripts/cfo_calc.py` — 10 deterministic calculators, stdlib only
- `assets/business-data-intake-template.csv` — 53-line intake sheet
- Three fully worked examples with verified arithmetic
- Data-quality problem table with detection and fix for 11 common issues

### Changed — structure

- Split a single 25,193-character file into a 6 KB router (`SKILL.md`) plus
  seven on-demand reference files. v1.0 loaded everything into context on every
  trigger.
- YAML frontmatter corrected: `name` before `description`, description tightened
  and made trigger-oriented, added `license` and `metadata`.
- Added a decision priority ladder with explicit tier-gating.
- Added four output templates sized to the request, so a one-line question no
  longer produces a twelve-section report.
- Benchmarks moved to their own file with explicit "orientation not standard"
  framing and a "what this file cannot tell you" section.

### Added — portability

- `platforms/universal-compact-core.md` at 7,529 characters, verified to fit
  the OpenAI Custom GPT 8,000-character instruction cap. v1.0 at 25,193
  characters could not be installed there at all.
- Adapters generated from that single source for Cursor (.mdc), Windsurf,
  GitHub Copilot, Gemini Gems, AGENTS.md, and plain system prompts.
- Install instructions for 12 platforms in `README.md`.

## 1.0.0

Initial single-file version.

---

*Md Kamrul Hasan · https://github.com/Kamrul5242 · signature `MKH-EBIC-2.1.0`*
