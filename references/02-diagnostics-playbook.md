# Diagnostics Playbook

Read this after computing the numbers. It converts metrics into a diagnosis and
a prescription.

## Contents
1. [Pattern recognition](#1-pattern-recognition)
2. [Root-cause trees](#2-root-cause-trees)
3. [Financial health scorecard](#3-financial-health-scorecard)
4. [Risk register](#4-risk-register)
5. [Scenario and sensitivity method](#5-scenario-and-sensitivity-method)
6. [Pricing decisions](#6-pricing-decisions)

---

## 1. Pattern recognition

Match the business to one pattern. If two apply, the one higher in this list
wins — it is the more urgent condition.

### Pattern A — Cash Emergency
`Net cash flow negative · Runway < 3 months`
Nothing else matters yet. Actions: list every cash outflow ranked by size and
cancellability; halt discretionary spend; accelerate receivables; renegotiate
supplier terms; determine the minimum revenue that reaches cash break-even.
**Do not discuss growth, branding, or hiring in this state.**

### Pattern B — Negative Unit Economics
`Contribution margin per order ≤ 0` or `CAC > LTV`
Every additional sale destroys value. Scaling is actively harmful.
Actions: rebuild the per-unit cost stack line by line; test price increase; cut
the worst-performing acquisition channel; check refund/RTO drag; verify COGS
includes landed cost, not invoice cost.

### Pattern C — Profitable on Paper, Cash Poor
`Net profit positive · Cash declining`
Cause is almost always working capital. Actions: compute CCC; check DSO for
slow collections; check inventory days for trapped cash; check whether loan
principal repayment or owner drawings are consuming cash below the profit line;
check capex.

### Pattern D — High ROAS, Weak Profit
`ROAS strong · Net margin thin or negative`
Actions: compute break-even ROAS (`1 / CM ratio before ads`) and compare.
Compute MER against platform ROAS — a gap means attribution is over-claiming.
Rebuild CM after ads, fees, shipping, refunds, packaging.

### Pattern E — Revenue Up, Profit Down
`Revenue ↑ · Net profit ↓`
Actions: decompose. Is it price (discounting), mix (shift to low-margin SKUs),
cost (COGS inflation), or overhead (fixed costs added ahead of revenue)?
Quantify each contribution. Usually one dominates.

### Pattern F — Growth Stalled, Profit Stable
`Revenue flat · Margins healthy`
Actions: check retention and repeat rate before assuming an acquisition problem.
Check market saturation, channel concentration, and whether the offer has aged.

### Pattern G — Healthy Growth
`Revenue ↑ · Profit ↑ · Cash ↑ · CAC stable · Retention holding`
Actions: identify the constraint that breaks first at 2× volume — cash,
inventory lead time, fulfilment capacity, or support. Scale toward that limit
deliberately. Protect the margin structure that produced the result.

### Pattern H — Concentration Fragility
`One customer > 20% of revenue` or `one channel > 60% of acquisition` or
`one supplier > 50% of spend`
Metrics may look excellent. The business is one email away from collapse.
Actions: quantify the loss scenario, then diversify deliberately.

---

## 2. Root-cause trees

**"Profit is falling"**
```
Falling profit
├─ Gross margin down?
│   ├─ Price down → discounting depth/frequency, mix shift to cheap SKUs
│   └─ COGS up → supplier price, FX, freight, duty, yield/waste, RTO losses
└─ Gross margin flat?
    ├─ OPEX up → headcount, rent, software creep, agency fees
    └─ Ad cost up → CPM inflation, CVR decline, creative fatigue, audience burn
```

**"Cash is disappearing but we're profitable"**
```
Cash gap
├─ Receivables rising      → DSO up, customers paying slower
├─ Inventory rising        → overbuying, slow SKUs, dead stock
├─ Payables falling        → paying suppliers faster than before
├─ Debt principal repaid   → below the P&L line, invisible in profit
├─ Capex                   → equipment, deposits, fit-out
└─ Owner drawings          → not an expense, still cash out
```

**"Ads aren't working"**
```
Ad problem
├─ Traffic quality?     → audience, placement, CPM vs relevance
├─ Landing page?        → bounce, load speed, mobile, trust signals
├─ Offer?               → price point, bundle, guarantee, urgency
├─ Checkout?            → payment options, COD, shipping cost shock
└─ Economics?           → is ROAS above break-even ROAS at all?
```

---

## 3. Financial health scorecard

Grade only what the data supports. **Write "insufficient data" rather than
guessing** — a fabricated grade is worse than a gap.

| Area | Metric used | Grade | Why |
|---|---|---|---|
| Revenue growth | MoM / YoY % | Strong / Watch / Weak | |
| Gross margin | GM % vs sector norm | | |
| Contribution margin | CM after ads | | |
| Net margin | Net % | | |
| Operating cash flow | OCF sign and trend | Positive / Neutral / Negative | |
| Liquidity | Current & quick ratio | | |
| Runway | Months | | |
| CAC efficiency | CAC, payback months | | |
| LTV:CAC | Ratio + payback | | |
| Retention | Repeat rate / NRR | | |
| Break-even | Above / Near / Below | | |
| Leverage | D/E, DSCR | Low / Moderate / High | |
| Concentration | Customer, supplier, channel % | | |
| Overall risk | Composite | | |

**Methodology rule:** state the threshold used for each grade. "Weak" without a
stated boundary is an opinion wearing a metric's clothes.

---

## 4. Risk register

Assess each category. Score likelihood × impact. Never declare a business
"low risk" without walking the whole list.

| Category | Look for |
|---|---|
| **Cash / liquidity** | Runway, DSCR, covenant breach, seasonal trough |
| **Unit economics** | CM ≤ 0, CAC rising faster than LTV |
| **Customer** | Concentration, churn spike, refund abuse |
| **Supplier** | Single source, lead time, FX, MOQ, quality |
| **Platform** | Marketplace/ad-account/payment-processor dependency, policy bans |
| **Inventory** | Dead stock, obsolescence, seasonality mismatch |
| **Currency** | Revenue and cost in different currencies, no hedge |
| **Regulatory / tax** | Registration, VAT/GST, customs, licensing, data rules |
| **Key person** | Founder-dependency, undocumented processes |
| **Operational** | Capacity ceiling, defect rate, fulfilment failure |
| **Cyber / fraud** | Account compromise, chargebacks, data loss |
| **Competitive** | Price war, new entrant, channel commoditization |

Output format per risk: **what could happen · likelihood · currency impact ·
early warning signal · mitigation.**

---

## 5. Scenario and sensitivity method

**Three scenarios, always:**

| | Conservative | Base | Aggressive |
|---|---|---|---|
| Revenue | −20 to −30% | Most likely | +20 to +30% |
| COGS % | +3 to +5 pts | Current | −2 pts |
| CAC | +25% | Current | −15% |
| Churn / refunds | Higher | Current | Lower |

Compare across scenarios: revenue, gross profit, contribution margin, net
profit, net cash flow, runway, break-even date.

**Sensitivity — find the two variables that matter most.** Flex each ±10% while
holding others constant, and rank by resulting change in net profit or cash.
Typical high-leverage variables: price, conversion rate, COGS, CAC, churn,
refund rate.

**Never assume price elasticity.** Compute the break-even volume loss instead:

```
Max volume loss tolerable on a price increase
= Price increase % / (CM ratio + Price increase %)
```

Example: 40% CM, 10% price rise → you can lose 20% of volume and still be
even. That is a fact about arithmetic, not a prediction about customers — but
it tells the founder how much risk the decision actually carries.

---

## 6. Pricing decisions

Work the questions in this order:

1. What is contribution margin at the current price, after **all** variable cost?
2. What does profit look like at +5%, +10%, +20%?
3. How much volume can be lost before profit falls? (formula above)
4. Is discounting buying repeat customers, or just donating margin?
5. Is there a tier or bundle that raises AOV without raising CAC?

Approaches: cost-plus · value-based · competitive · premium · penetration ·
freemium · tiered · bundled · dynamic.

**Never set price from competitor price alone.** Competitors may have different
cost structures, different volumes, or be losing money.

---

*Diagnostics playbook — skill by **Md Kamrul Hasan** ·
https://github.com/Kamrul5242*
