# Data Intake and Handling Incomplete Data

Most founders do not arrive with clean books. This file covers extraction,
validation, and what to do when data is thin.

---

## 1. Intake checklist

For every number captured, record six attributes:

| Attribute | Example |
|---|---|
| Value | 850,000 |
| Currency | BDT |
| Period | March 2026, monthly |
| Category | Net revenue |
| Source | User-stated / platform export / estimated |
| Confidence | Actual / Estimated / Assumed |

Restate the extracted table back to the user before computing when the input
was messy, a screenshot, or pasted unstructured text.

---

## 2. Minimum data by question

| The user asks | Minimum required |
|---|---|
| Am I profitable? | Revenue, COGS, **per-order variable costs**, **ad spend**, fixed overhead |
| Cash in / cash out | Inflow list, outflow list, period — or, from a P&L: net profit, D&A, changes in AR/inventory/AP, capex, loan principal, drawings |
| Runway | Cash balance, monthly net burn |
| Break-even | Fixed costs, price, variable cost per unit |
| Unit economics | Price, variable costs, orders, acquisition spend, new customers |
| Should I scale ads? | Contribution margin before ads, current ROAS/MER |
| Should I raise price? | Price, variable cost per unit, current volume |
| Valuation | Revenue, EBITDA, growth rate, comparable set |
| Can I afford this loan? | Operating cash flow, existing debt service, new terms |
| Should I take this investment? | Pre-money, amount, current cap table |

If a required input is missing, name it precisely:
> "I can't compute runway. I need your current cash balance and monthly fixed
> costs. Everything else you gave me is enough."

Never substitute a guess for a missing input and present the result as fact.

---

## 3. Common data problems and the fix

| Problem | Detection | Fix |
|---|---|---|
| Mixed periods | Monthly cost vs annual revenue | Normalize to one period, state which |
| Revenue vs cash confusion | "Revenue" includes unpaid invoices | Split billed vs collected |
| Gross vs net revenue | Refunds not deducted | Ask; if unknown, label basis used |
| Ad spend double-counted | In both COGS and OPEX | Put it in exactly one place. With `cfo_calc.py` use `--adspend`, and leave it out of `--opex` and `--cogs` |
| Owner salary missing | Net margin looks impossibly good | Add market-rate owner comp; note it |
| COGS = invoice cost only | Imported goods, no freight/duty | Reconstruct landed cost |
| Inventory as expense | Purchases treated as COGS | Adjust for opening/closing stock |
| Loan principal as expense | Profit understated, cash right | Split interest (P&L) from principal (cash) |
| VAT included in revenue | Revenue inflated | Strip tax to get net revenue |
| Platform-reported ROAS | Over-attribution | Cross-check against blended MER |
| Cohort too young for LTV | Lifetime assumed, not observed | Use observed period value; label it |

---

## 3b. Mapping the intake sheet onto `cfo_calc.py`

`assets/business-data-intake-template.csv` has more cost sections than the
calculator has flags. Fold them like this — **every row lands in exactly one
flag**:

| CSV section | Rows | `margins` flag |
|---|---|---|
| INCOME | Gross Revenue | `--revenue` |
| INCOME | Returns & Refunds, Discounts | `--returns` |
| COGS | Product cost, inbound freight, duty, direct labour, packaging | `--cogs` |
| VARIABLE | Outbound shipping, payment gateway, marketplace commission, RTO | `--variable` |
| OPEX | Advertising Spend | `--adspend` |
| OPEX | Salaries, owner comp, rent, software, utilities, professional fees | `--opex` |
| OPEX | Depreciation & Amortization | `--depreciation` / `--amortization` |
| BELOW_LINE | Interest, Tax | `--interest`, `--tax` |

**The single most common error is dropping the VARIABLE section.** Shipping,
gateway fees and RTO routinely total 15–20% of net revenue in COD e-commerce.
Omitting them, and putting ad spend nowhere, turns a loss into an apparent
profit — the worked example in `06-worked-examples.md` swings from −৳160,750
to +৳228,000 that way.

For per-unit work, variable cost per order =
`(COGS + VARIABLE) ÷ orders`, **not** `COGS ÷ orders`.

---

## 4. Estimating responsibly

When estimation is unavoidable:

1. **Say it is an estimate**, in the sentence where the number appears.
2. **Show the basis** — "assuming a 5% refund rate typical for apparel."
3. **Give a range, not a point** — "roughly ৳40,000–55,000."
4. **Test sensitivity** — if the conclusion flips within the range, say so
   loudly: *"If your refund rate is above 8%, this becomes unprofitable."*
5. Mark every estimated figure `(assumed)` in tables.

**Never estimate:** tax rates, legal obligations, current exchange rates,
current ad platform costs, or a specific competitor's margins. Look these up or
decline.

---

## 5. Handling a screenshot or pasted dashboard

1. Read out every value found and its label.
2. Flag anything ambiguous — "Sales" could be gross or net; ask which.
3. Check that the total equals the sum of the parts.
4. Check the date range shown on the dashboard against the period the user is
   asking about; platforms default to windows that do not match the question.
5. Note attribution windows on ad platforms (7-day click vs 1-day) — they change
   ROAS materially.

---

## 6. When the user has almost nothing

Do not refuse. Do this instead:

1. Answer what the fragment supports.
2. Give the founder a short list of the exact numbers to collect next.
3. Offer the intake template at `assets/business-data-intake-template.csv`.
4. Show what the analysis would look like once those numbers exist.

A founder who leaves knowing which five numbers to track has received real
value even without a full report.

---

*Data intake reference — skill by **Md Kamrul Hasan** ·
https://github.com/Kamrul5242*
