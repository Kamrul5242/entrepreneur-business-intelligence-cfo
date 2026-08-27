# Formula Library

Every formula states its **inputs, units, and the mistake people make with it.**
Percentages are shown as `× 100` only where the output is meant to be read as a
percent; in downstream formulas always use the decimal form.

## Contents

1. [Income statement](#1-income-statement)
2. [Balance sheet](#2-balance-sheet)
3. [Cash flow](#3-cash-flow)
4. [Margins](#4-margins)
5. [EBITDA and earnings variants](#5-ebitda-and-earnings-variants)
6. [Break-even](#6-break-even)
7. [Unit economics](#7-unit-economics)
8. [Marketing and funnel](#8-marketing-and-funnel)
9. [Growth and recurring revenue](#9-growth-and-recurring-revenue)
10. [Liquidity and solvency](#10-liquidity-and-solvency)
11. [Working capital and the cash cycle](#11-working-capital-and-the-cash-cycle)
12. [Inventory](#12-inventory)
13. [Return and investment appraisal](#13-return-and-investment-appraisal)
14. [Valuation](#14-valuation)
15. [Funding and dilution](#15-funding-and-dilution)
16. [Debt](#16-debt)
17. [Operational efficiency](#17-operational-efficiency)

---

## 1. Income statement

This chain is the canonical one. `scripts/pl_model.py` defines it; the block
below is validated against that definition by
`scripts/test_reference_consistency.py`, which evaluates both on random inputs
and fails if they ever disagree. Do not edit one without the other.

<!-- canonical-bridge:start -->
```
Net Revenue        = Gross Revenue − Returns − Discounts
Gross Profit       = Net Revenue − COGS
Contribution       = Gross Profit − Variable Costs
Operating Profit   = Contribution − Ad Spend − Fixed OpEx − D&A
EBITDA             = Operating Profit + D&A
Pre-tax Profit     = Operating Profit − Interest
Net Profit         = Pre-tax Profit − Tax
```
<!-- canonical-bridge:end -->

**Denominator discipline:** this skill uses **Net Revenue** for every margin.
If the user only supplies gross revenue, say so and label margins as
"gross-revenue basis".

### Cost classification — every cost belongs to exactly one bucket

There is no "treat it as direct if you prefer" option. A cost placed in two
buckets is subtracted twice, and a cost in no bucket turns a loss into a
profit. This table is the classification; the intake template mirrors it.

<!-- canonical-buckets:start -->
| Term | Intake section | Line items |
|---|---|---|
| `COGS` | COGS | Product / Material Cost, Inbound Freight, Duty & Clearing, Direct Labour, Packaging |
| `VARIABLE` | VARIABLE | Outbound Shipping, Payment Gateway Fees, Marketplace Commission, RTO / Failed Delivery Cost |
| `AD_SPEND` | OPEX | Advertising Spend |
| `FIXED_OPEX` | OPEX | Salaries (non-production), Owner Compensation, Rent, Software & Subscriptions, Utilities, Professional Fees, Other Operating |
| `DNA` | OPEX | Depreciation & Amortization |
| `BELOW_LINE` | BELOW_LINE | Interest Expense, Tax |
<!-- canonical-buckets:end -->

**The trap:** `VARIABLE` is the bucket founders forget. Outbound shipping,
payment gateway fees, marketplace commission and RTO routinely total 15%% of
net revenue in COD e-commerce. Omitting them, and leaving ad spend out of the
chain, is precisely how the worked example in `06-worked-examples.md` would
read as **+৳228,000** instead of its true **−৳160,750**.

**Note on placement:** packaging is `COGS`, not `VARIABLE`. Payment processing
is `VARIABLE`, not `COGS`. Product cost is LANDED — ex-factory plus inbound
freight plus duty and clearing.

---

## 2. Balance sheet

```
Assets = Liabilities + Equity
```

If this does not hold, the data is wrong. Report the imbalance in currency
terms before continuing.

```
Working Capital = Current Assets − Current Liabilities
Net Debt        = Total Debt − Cash and Cash Equivalents
Book Equity     = Total Assets − Total Liabilities
```

Negative working capital is **not automatically bad** — subscription and
cash-on-delivery models often run negative by design. Judge against the cash
conversion cycle (§11).

---

## 3. Cash flow

```
Net Change in Cash = Operating CF + Investing CF + Financing CF
Net Cash Flow      = Total Cash Inflows − Total Cash Outflows
```

**Indirect method (when only P&L + balance sheet are available):**
```
Operating CF = Net Profit
             + Depreciation & Amortization
             + Other non-cash charges
             − Increase in Accounts Receivable
             − Increase in Inventory
             + Increase in Accounts Payable
             ± Other working capital changes
```

```
Free Cash Flow (firm)   = Operating CF − Capital Expenditure
Free Cash Flow (equity) = FCF − Net Debt Repayment
```

**Burn and runway:**
```
Gross Burn   = Total Cash Outflows per month
Net Burn     = Cash Outflows − Cash Inflows        (per month)
Runway (mo)  = Available Cash / Monthly Net Burn
```
Runway by simple division is only valid when burn is roughly stable. If burn is
growing, build a month-by-month forecast instead and report the month cash
crosses zero.

**Pitfall:** FCF ≠ profit. EBITDA ≠ FCF. Cash in bank ≠ any of them.

---

## 4. Margins

```
Gross Profit        = Net Revenue − COGS
Gross Margin %      = Gross Profit / Net Revenue × 100

Contribution        = Gross Profit − Variable Costs
CM per unit         = Price per unit − Variable Cost per unit
CM Ratio            = Contribution / Net Revenue

Operating Profit    = Contribution − Ad Spend − Fixed OpEx − D&A
Operating Margin %  = Operating Profit / Net Revenue × 100

Net Margin %        = Net Profit / Net Revenue × 100
```

**Gross margin vs contribution margin** — the most commonly confused pair.
Gross margin subtracts COGS only. Contribution additionally subtracts the
`VARIABLE` bucket — outbound shipping, payment gateway fees, marketplace
commission and RTO. Ad spend is subtracted after contribution, not inside it,
because break-even ROAS is measured against contribution before ads.

For any e-commerce or ads-driven business, **contribution margin after ads is
the number that decides whether to scale.** Gross margin will lie to you.

Report all four margins whenever the data allows.

---

## 5. EBITDA and earnings variants

```
EBIT   = Operating Profit
EBITDA = EBIT + Depreciation + Amortization
```

**D&A convention — unconditional.** In this skill D&A is always an
operating cost: it is subtracted to reach operating profit and added back to
reach EBITDA. `cfo_calc.py`, the workbook and every platform adapter follow
this. There is no variant where EBITDA equals operating profit.

Because D&A is its own term in the bridge, `Fixed OpEx` never contains it. In
`cfo_calc.py margins`, pass D&A through `--depreciation` / `--amortization`
and keep it out of `--opex`, or it is subtracted twice.

Alternative build-up:
```
EBITDA = Net Profit + Interest + Tax + Depreciation + Amortization
```

```
Adjusted EBITDA = EBITDA ± one-off, non-recurring, owner-discretionary items
```
Every adjustment must be listed. Unlisted add-backs are how valuations get
inflated.

**EBITDA is not:** net profit, free cash flow, distributable cash, or money in
the bank. For asset-heavy or inventory-heavy businesses it materially overstates
economic performance.

---

## 6. Break-even

```
CM per unit    = Price − Variable Cost per unit
BEP (units)    = Fixed Costs / CM per unit
CM Ratio       = CM per unit / Price
BEP (revenue)  = Fixed Costs / CM Ratio
```

**With a target profit:**
```
Units for target = (Fixed Costs + Target Profit) / CM per unit
```

**Margin of safety:**
```
Margin of Safety % = (Actual Sales − BEP Sales) / Actual Sales × 100
```

**Cash break-even** (excludes non-cash fixed costs — the number that matters
when survival is the question):
```
Cash BEP (units) = (Fixed Costs − D&A) / CM per unit
```

**Operating leverage:**
```
Degree of Operating Leverage = Contribution Margin / Operating Profit
```
High DOL means profit moves violently with volume — both directions.

---

## 7. Unit economics

The question: **does one customer, order, or product actually make sense?**

```
AOV  = Net Revenue / Number of Orders
ARPU = Revenue / Active Users            (state the period: monthly ARPU, etc.)
```

**Customer acquisition cost — always state which one:**
```
Paid CAC    = Paid Marketing Spend / New Customers from Paid
Blended CAC = (All Sales & Marketing Cost) / All New Customers
Fully-loaded CAC = Blended CAC + sales salaries + tools + agency + creative
```
A founder quoting a healthy CAC is usually quoting paid CAC while paying
blended costs. Ask which one, or compute both.

**Lifetime value — unit-disciplined form:**
```
LTV = ARPU_period × Gross Margin (decimal) × Expected Lifetime (in the same periods)
```
Example: ৳2,000 monthly ARPU × 0.45 margin × 18 months = ৳16,200.
`ARPU_period` and `Expected Lifetime` **must use the same period unit.** This is
where the original version of this skill was ambiguous.

**Churn-derived form (subscription only, requires reliable churn):**
```
Expected Lifetime (months) = 1 / Monthly Churn Rate (decimal)
LTV = (ARPU_monthly × Gross Margin) / Monthly Churn Rate
```
Invalid when churn is near zero, when the cohort is under ~6 months old, or when
churn is not roughly constant. Say so rather than producing a fantasy LTV.

**Repeat-purchase form (e-commerce):**
```
LTV = AOV × Gross Margin × Purchases per Customer per Year × Retained Years
```

**Ratios:**
```
LTV : CAC = LTV / CAC
CAC Payback (months) = CAC / (Monthly Contribution Profit per Customer)
```
Do not apply "3:1 is good" mechanically. A 3:1 with 24-month payback and no
cash is worse than 2:1 with 2-month payback. Judge by margin, payback, retention
confidence, and funding position.

---

## 8. Marketing and funnel

```
CTR             = Clicks / Impressions × 100
CPC             = Ad Spend / Clicks
CPM             = Ad Spend / Impressions × 1000
CPL             = Ad Spend / Leads
CPA / CPP       = Ad Spend / Purchases
Conversion Rate = Conversions / Relevant Denominator × 100
```
**Always name the denominator.** Visitor→buyer, lead→customer, and
checkout→purchase are three different numbers. Never mix them in one comparison.

```
ROAS = Ad-attributed Revenue / Ad Spend            (a multiple, e.g. 4.0x)
MER  = Total Revenue / Total Marketing Spend       (blended, platform-agnostic)
```
MER is harder to game than platform-reported ROAS. When channel ROAS looks
great but MER is flat, the platform is claiming credit for organic sales.

**Break-even ROAS — the number that decides whether an ad account is viable:**
```
Break-even ROAS = 1 / Contribution Margin Ratio (before ad cost)
```
Example: 40% CM before ads → break-even ROAS = 2.5x. A 3.0x ROAS is profitable;
a 2.0x ROAS is burning money regardless of how good the dashboard looks.

```
Marketing ROI % = (Gross Profit from Marketing − Marketing Cost) / Marketing Cost × 100
```

**Funnel:**
```
Traffic → Lead → Qualified Lead → Checkout/Call → Customer → Repeat
```
Compute the step-to-step conversion at every stage, identify the single largest
drop, and fix that before increasing spend. **Never recommend more ad spend into
a leaking funnel.**

---

## 9. Growth and recurring revenue

```
Growth Rate %   = (Current Period − Prior Period) / Prior Period × 100
CAGR %          = ((Ending / Beginning)^(1 / Years) − 1) × 100
Run Rate        = Period Revenue × Periods per Year      ← label as annualized, not forecast
```

```
MRR  = Sum of normalized monthly recurring revenue
ARR  = MRR × 12
```

```
Customer Churn % = Customers Lost / Customers at Start × 100
Revenue Churn %  = Revenue Lost  / Revenue at Start   × 100
Gross Revenue Retention % = (Start Rev − Churn − Contraction) / Start Rev × 100
Net Revenue Retention %   = (Start Rev − Churn − Contraction + Expansion) / Start Rev × 100
```
GRR caps at 100%. NRR above 100% means expansion is outrunning losses.
**Customer retention and revenue retention are different questions.**

```
Quick Ratio (SaaS) = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
Rule of 40         = Growth Rate % + Profit Margin %      (SaaS heuristic only)
```

---

## 10. Liquidity and solvency

*Missing entirely from v1 — this is what the health scorecard actually grades.*

```
Current Ratio = Current Assets / Current Liabilities
Quick Ratio   = (Current Assets − Inventory) / Current Liabilities
Cash Ratio    = Cash and Equivalents / Current Liabilities
```
Rough reading: current ratio under 1.0 signals short-term stress; quick ratio is
the honest version for inventory-heavy businesses, because stock is not cash.

```
Debt-to-Equity     = Total Debt / Total Equity
Debt-to-Assets     = Total Debt / Total Assets
Net Debt / EBITDA  = (Total Debt − Cash) / EBITDA
Equity Ratio       = Total Equity / Total Assets
```

```
Interest Coverage = EBIT / Interest Expense
DSCR              = Operating Cash Flow (or EBITDA) / Total Debt Service
```
Debt service = principal + interest due in the period. Lenders commonly want
DSCR above ~1.25, but never quote a threshold without naming industry and
lender context.

---

## 11. Working capital and the cash cycle

```
DIO = (Average Inventory / COGS) × Days in Period
DSO = (Average Accounts Receivable / Credit Sales) × Days in Period
DPO = (Average Accounts Payable / COGS or Purchases) × Days in Period

Cash Conversion Cycle = DIO + DSO − DPO
```

CCC is the number of days cash is trapped between paying suppliers and
collecting from customers. Multiply the improvement by daily COGS to express a
CCC reduction in currency:

```
Cash released = Days improved × (COGS / Days in Period)
```

Lower CCC is generally better, but a negative CCC achieved by stretching
suppliers is borrowed, not earned. Check supplier relationship risk.

---

## 12. Inventory

```
Inventory Turnover = COGS / Average Inventory
Average Inventory  = (Opening + Closing) / 2
Days Inventory     = 365 / Inventory Turnover
Sell-through %     = Units Sold / (Units Received) × 100
GMROI              = Gross Profit / Average Inventory Cost
Stock-to-Sales     = Inventory Value / Sales Value
```

```
Landed Cost per unit = Ex-factory + Freight + Duty + Clearing + Inbound handling
                       ────────────────────────────────────────────────────────
                                          Units received
```
Landed cost — not invoice cost — is the correct COGS input for imported goods.

```
Dead stock value = Units with zero movement in N days × Landed Cost
```
Dead stock is cash on a shelf. Value it and name it.

---

## 13. Return and investment appraisal

```
ROI %  = (Net Gain from Investment / Cost of Investment) × 100
ROIC % = NOPAT / Invested Capital × 100          NOPAT = EBIT × (1 − Tax Rate)
ROE %  = Net Profit / Average Equity × 100
ROA %  = Net Profit / Average Total Assets × 100
```
Always state which profit figure and which period. ROI over 3 years is not
comparable to ROI over 3 months without annualizing.

**Payback period:**
```
Payback (periods) = Initial Investment / Net Cash Inflow per Period
```
For uneven flows, accumulate until cumulative cash turns positive and
interpolate.

**Net present value** *(missing from v1 despite DCF being promised)*:
```
NPV = Σ [ CFt / (1 + r)^t ] − Initial Investment
```
where `CFt` = net cash flow in period t, `r` = discount rate per period.
NPV > 0 → creates value at that discount rate.

**IRR:** the rate `r` where NPV = 0. Solve numerically — use
`scripts/cfo_calc.py`, do not estimate by eye.

**Discount rate:**
```
WACC = (E/V × Re) + (D/V × Rd × (1 − Tax Rate))
```
E = equity value, D = debt value, V = E + D, Re = cost of equity, Rd = cost of
debt. For a small private business, using the founder's realistic alternative
return (or the cost of the loan they'd otherwise take) is more honest than a
fabricated CAPM. **State the rate and why it was chosen.**

---

## 14. Valuation

```
Enterprise Value = Equity Value + Total Debt − Cash
Equity Value     = Enterprise Value − Total Debt + Cash
```

**Multiples:**
```
EV / Revenue   EV / EBITDA   EV / Gross Profit   P/E = Price / Earnings
```
A multiple is only meaningful against genuinely comparable businesses — same
model, similar growth, similar margin, similar size, similar market. State the
comparable set and the source. Never present a generic multiple as a valuation.

**DCF:**
```
Value = Σ [ FCFt / (1 + WACC)^t ] + Terminal Value / (1 + WACC)^n

Terminal Value (Gordon growth) = FCF_(n+1) / (WACC − g)
```
Requires `WACC > g`. Terminal value usually dominates the result, so state `g`
explicitly and test sensitivity to it. For an early-stage or volatile business,
DCF output is a range, not a number.

**Value drivers to comment on:** growth rate, margin quality, revenue
recurrence, customer concentration, owner dependency, market size, defensibility.

---

## 15. Funding and dilution

```
Post-money Valuation = Pre-money Valuation + New Investment
Investor Ownership % = New Investment / Post-money Valuation × 100
Founder Ownership after = Founder Ownership before × (1 − Dilution %)
Price per Share = Pre-money Valuation / Pre-money Fully Diluted Shares
```

**Option pool shuffle:** if the pool is created pre-money, founders absorb the
full dilution. Always state whether the pool sits pre or post.

**SAFE / convertible note:**
```
Conversion Price = min( Valuation Cap / Fully Diluted Shares ,
                        Round Price × (1 − Discount) )
```
Model the cap-table effect at conversion, not just at signing. Explain dilution
from the founder's seat in absolute ownership and in value terms.

---

## 16. Debt

```
EMI = P × r × (1 + r)^n / ((1 + r)^n − 1)
```
P = principal, r = **periodic** rate (annual / 12 for monthly), n = number of
periods.

```
Total Interest = (EMI × n) − P
Effective Annual Rate = (1 + Nominal Rate / m)^m − 1        m = compounds/year
```

```
Debt Service Coverage = Operating Cash Flow / (Principal + Interest due)
```
Before recommending debt, confirm the business can service it from operating
cash flow in the **conservative** scenario, not the base case.

---

## 17. Operational efficiency

```
Revenue per Employee      = Net Revenue / FTE
Gross Profit per Employee = Gross Profit / FTE
Orders per Employee       = Orders / FTE
Refund Rate %             = Refunds / Orders × 100
RTO Rate %                = Returned-to-origin Orders / Shipped Orders × 100
Fulfilment Cost per Order = Total Fulfilment Cost / Orders
Support Cost per Order    = Total Support Cost / Orders
Capacity Utilization %    = Actual Output / Maximum Output × 100
Supplier Concentration %  = Largest Supplier Spend / Total Supplier Spend × 100
Customer Concentration %  = Largest Customer Revenue / Total Revenue × 100
```

Customer concentration above ~20% from one account, or supplier concentration
above ~50% from one vendor, is a material risk that belongs in the risk section
regardless of how good the margins look.

---

*Formula library — Entrepreneur Business Intelligence & CFO skill by
**Md Kamrul Hasan** · https://github.com/Kamrul5242*
