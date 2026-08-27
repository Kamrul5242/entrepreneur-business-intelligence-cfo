# Changelog

## 2.2.1 — 2026-08-27

A correctness and reliability release. No new capability.

### Fixed — depreciation was silently ignored by `margins` (CRITICAL)
- `scripts/cfo_calc.py` `margins()` never subtracted depreciation or
  amortization from operating profit; it only added them back for EBITDA. The
  same business therefore reported a profit **higher by exactly the D&A
  amount** through `margins` than through `intake`, and higher than the
  workbook, whose Dashboard operating profit subtracts TOTAL OPEX including
  the D&A row. On the audit case: `margins` said 200,000, `intake` and the
  workbook said 150,000. `net_profit` inherited the overstatement and EBITDA
  compounded it. D&A is now subtracted from operating profit and added back
  for EBITDA, and `--opex` documents that it EXCLUDES D&A so the two cannot be
  double counted. `depreciation_amortization` is reported explicitly.

### Fixed — runway was measured from the wrong cash balance (HIGH)
- `intake` divided the OPENING cash balance by the burn, overstating survival
  by a full period. With opening 1,000,000, closing 600,000 and a 40,000 burn
  it reported 25 months instead of 15. It now uses closing cash when a closing
  balance exists, falls back to opening only when it does not, and names the
  basis in `runway_basis` and `runway_cash_used`.

### Fixed — `intake` silently added different currencies together (HIGH)
- A sheet holding 100,000 BDT and 500 USD produced a single "BDT" net revenue
  of 99,500 with no warning, in breach of the skill's own rule against summing
  mixed currencies. `intake` now refuses: it reports every currency found and
  where, and returns no P&L until the sheet is normalised to one currency. No
  exchange rate is ever assumed. Unit counts (`count`) are not mistaken for a
  currency, and a balance-sheet date is not mistaken for a mixed period.
- Income-statement rows spanning more than one period now raise an ALERT
  listing the periods; balance-sheet rows are exempt, being a point in time.

### Fixed — smaller defects that made output read more certain than it was
- The workbook error reporter crashed with `TypeError` the moment it found an
  error, because `Address` is a property, not a method on this binding. It now
  names the offending cells, verified by injecting `=1/0` and `=NA()`.
- `intake` discarded the `confidence` column. Non-`actual` rows are now listed
  in `estimated_inputs`, as hard rule 4 requires.
- `runway` called an overdrawn account "CASH POSITIVE" when the balance was
  negative but no longer falling. It now says OVERDRAWN.
- `roas` treated a ROAS of exactly 0 as missing and reported no headroom, so a
  campaign that returned nothing showed no gap to break-even.
- `cac` reported a CAC of 0 with a silent `null` ratio; it now explains that
  LTV:CAC is undefined rather than infinite.

### Changed
- All seven platform adapters and the reference formula library now define
  `EBIT = Contribution − Ad Spend − Fixed OpEx − D&A`, replacing the
  conditional "[only if D&A sits in OpEx]" wording that allowed the ambiguity.
- Tests: 57 calculator (was 33) and 13 workbook (was 12). Every new test was
  verified to FAIL against the pre-fix code before being accepted.

## 2.2.0 — 2026-08-27

### Fixed — documentation drift outside README
- `llms.txt` and `CITATION.cff` still described a 5-sheet, 90-formula workbook
  and a 10-command calculator. `llms.txt` is the file AI crawlers read, so
  automated reviewers kept reporting the old figures long after README was
  corrected — the drift was real, not a stale cache. Both now match the
  shipped artifact, and `llms.txt` lists the test scripts, the intake example
  and the current command set.
- `build_dashboard.py` still carried a KNOWN ISSUE docstring saying its own
  output could not be opened by Excel. That was fixed in this release; the
  docstring now documents determinism and the font-name constraint instead.

### Added — the workbook build is reproducible
- Two runs of `build_dashboard.py` now produce byte-identical files, so the
  committed workbook can be rebuilt from source and still verify against
  `SIGNATURE.json`. An `.xlsx` is a ZIP: entry timestamps and the
  `dcterms:modified` field openpyxl writes at save time are both pinned.
  `SOURCE_DATE_EPOCH` overrides the fixed stamp.
- Two new tests enforce it: one asserts two builds are byte-identical, the
  other asserts a rebuild reproduces the committed workbook exactly.

### Added — automated Excel testing
- New `scripts/test_workbook_excel.py`, 10 tests in two layers. The structural
  layer uses openpyxl only and runs anywhere: it rejects font names that are
  not a single family, rejects conditional-format fills that omit `bgColor`,
  and pins the sheet list and formula count. The engine layer drives real Excel
  through COM, recalculates every formula, asserts no cell evaluates to an
  error, and cross-checks Excel's Dashboard figures against `cfo_calc.py` on
  identical inputs — two independent implementations agreeing on −৳160,750.
- Both regression guards were validated by reintroducing the original bugs:
  the font-stack build fails the name check *and* Excel refuses to open it, and
  the `fgColor` build fails both the styles-XML check and an Excel
  `DisplayFormat` check showing the status pill is white text on white.
- `CFO_WORKBOOK` points the tests at any workbook, so a rebuild can be verified
  before it is committed. `openpyxl` reports `dxf.fill` as `None` on read, so
  the fill check reads `xl/styles.xml` directly.

### Fixed — the workbook could not be rebuilt at all
- `SYMFONT` was `"Noto Sans,FreeSans,Arial Unicode MS,Arial"` — a CSS-style font
  stack. An Excel font name must be a single family of at most 31 characters and
  may not contain commas, so every rebuild produced a workbook Excel refused to
  open, repair mode included. The shipped binary predated that line, so the
  defect stayed latent until the workbook was rebuilt. Now `Nirmala UI`, which
  also renders Bangla. Isolated by ablation: values-only rebuilds opened, and
  re-applying fonts alone broke them again.
- Conditional-format fills were written as `PatternFill("solid", fgColor=…)`.
  Excel renders differential-format fills from `bgColor`, so the RED/GREEN status
  pills on the Dashboard and Scenarios sheets were bold white text on no fill —
  invisible since they were introduced. Now `PatternFill(bgColor=…)`.
- The Start Here intro paragraph was styled to wrap across A:H but never merged,
  so it wrapped inside column A and was clipped.

### Added — the workbook now explains itself
- New sheet **0. Start Here**, opening first: what the workbook is, three
  steps, the eight numbers that actually matter (with plain-English meanings
  and where to find each one), a guide to every sheet, a warning that profit
  is not cash, and a Bangla summary. The workbook previously opened on a
  Setup sheet with thirty-eight input fields and no indication which mattered.
- The eight essential inputs on **1. Setup** now carry a gold `◀ START HERE`
  marker in column C. Column C was empty, so no formula reference moved.
- Sheet tabs are colour-coded: gold for the guide, green for the sheet you
  type into, navy for the answer, grey for reference.
- These are additive only — the 161 formulas and every cell reference are
  unchanged, verified by re-evaluating the Trend sheet's formulas after the
  rebuild.

### Added — the intake sheet is now executable
- New `intake` command: `cfo_calc.py intake --file <filled-template>.csv`
  reads the intake sheet and runs the whole chain in one call — P&L, unit
  economics, acquisition, marketing, cash reconciliation, working capital,
  balance-sheet tie-out, concentration, and the five answers required by
  `SKILL.md` §5. Previously the sheet's eleven sections had to be hand-mapped
  onto two calculator flags, which is how a −৳160,750 loss got reported as a
  +৳228,000 profit.
- New `assets/business-data-intake-example.csv` — the `06-worked-examples.md`
  business filled in. `intake` on it reproduces the hand-written analysis
  exactly, including the verdict that fixed costs, not ad efficiency, are the
  binding problem.
- New `inventory` command: turnover, days of stock, sell-through, GMROI, dead
  stock, safety stock, reorder point, EOQ and contribution lost to stockouts.
  `05-ecommerce-and-inventory.md` §7 listed these; nothing computed them.
  Safety stock states its own basis, and says so plainly when it is zero
  because no variability input was given.
- New sheets **0. Start Here** and **4. Trend** now ship in the workbook, which
  goes from 5 sheets / 90 formulas to 7 sheets / 161. Verified in Excel:
  0 formula errors across all seven sheets, and Excel's own engine returns
  contribution 259,250 and operating profit −160,750 for the worked example.
- All seven screenshots in `docs/screenshots/` are regenerated, exported from
  the shipped workbook by Excel itself.
- New `requirements.txt` pinning `openpyxl==3.1.5`. The calculator and its
  tests remain standard-library only; the pin exists because openpyxl changes
  the archive layout between releases, which changes the workbook's SHA-256
  and breaks the manifest match even when the content is identical.

### Changed
- Version and signature ID moved together to `MKH-EBIC-2.2.0`. The ID embeds
  the version, so leaving it at 2.1.0 would misstate provenance.
- `platforms/system-prompt.txt` and `platforms/gemini-gem-instructions.md`
  are no longer byte-identical copies of `universal-compact-core.md`; each is
  now written for its own target format.

### Fixed in this release

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

### Added — cost completeness
- `margins` gained `--variable` (outbound shipping, payment gateway,
  marketplace commission, RTO) and `--adspend`. Previously the intake
  template's whole VARIABLE section had nowhere to go, and the docstring
  example demonstrated a mapping that reported **+৳228,000** for the
  `06-worked-examples.md` business whose true result is **−৳160,750**. All
  three commands now agree on −৳160,750.
- `margins` warns when `--variable` or `--adspend` is absent. Passing `0`
  explicitly confirms there are none and silences it; absence and zero are
  no longer conflated.
- `unit` gained `--adspend`, plus `break_even_units_incl_ad_spend`,
  `total_contribution_after_ads` and `ad_cost_per_unit`. Margin of safety is
  now measured against break-even *including* ad spend: the worked-example
  store moves from an apparent **+30.6%** cushion to its real **−62.0%**.
  Without `--adspend` the field is named `operating_profit_before_ad_spend`,
  because a number that omits a cost should not be called operating profit.
- New `cashflow` command — indirect method: operating, investing and
  financing cash flow, profit-to-cash gap, optional opening/closing cash
  reconciliation. `SKILL.md` §7 and Example 2 previously had no tool support
  at all. Reproduces Example 2 exactly (OCF −৳85,000, net −৳555,000).
- `roas` verdict now reads `PROFITABLE on ads (before fixed costs)` and
  carries a note that fixed overhead has not been deducted.
- New `scripts/test_cfo_calc.py` — 33 stdlib regression tests covering the
  three worked examples, the intake sheet end to end, and business-invalid
  input. The repository previously had no tests; a parser-construction test
  would have caught the Python 3.13 crash.

### Fixed — business-invalid input crashed instead of explaining
- `npv --rate -1`, `loan --months 0`, `dilution` with a zero post-money, and
  `price-test --price 0` all raised ZeroDivisionError or TypeError. Each now
  returns a plain-language ERROR.
- `margins` now ALERTs when net revenue is zero or negative — previously it
  returned neat but meaningless margin percentages against a negative
  denominator, e.g. when refunds exceeded sales.

### Fixed — guidance that caused the wrong answer
- `references/07-data-intake.md` listed the minimum data for "Am I
  profitable?" as revenue, COGS and operating expenses. That omits per-order
  variable costs and ad spend and is the doc-level origin of the sign flip.
  Corrected, and a new §3b maps every intake-CSV section onto the exact
  calculator flag.
- The same file said to place ad spend in OPEX, which would double-count
  against the new `--adspend`. It now names one destination.
- `SKILL.md` gained hard rule 8: a profit computed from revenue, COGS and
  OPEX alone is not a profit, and any missing cost bucket must be named in
  the same sentence as the number.

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

*Md Kamrul Hasan · https://github.com/Kamrul5242 · signature `MKH-EBIC-2.2.0`*
