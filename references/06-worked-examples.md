# Worked Examples

Three complete analyses showing the expected depth, structure, and tone.
All arithmetic here is verified — reproduce this standard.

---

## Example 1 — "My ROAS is 3.5x, why am I broke?"

### Input given by the user
Gross revenue ৳920,000/month · returns ৳70,000 · COGS ৳442,000 · ad spend
৳240,000 · 1,700 orders · payment gateway 2.5% · shipping ৳60/order ·
packaging ৳15/order · fixed costs ৳180,000/month.

### Step 1–2 — Extract and validate
All figures monthly, BDT, actual. Note: the user's "3.5x ROAS" is platform-
reported. Blended MER computed below for comparison. Returns are already
excluded from net revenue, so no separate refund provision is applied.

### Step 3 — Calculate

> **Using `cfo_calc.py` for this example:** no single command produces the
> figure below. `margins` has no input for ad spend or per-order fees, and
> `unit` has no input for ad spend, so each returns a *profit* for this
> business. Build the variable stack first, then chain:
> `unit --price 500 --varcost 347.5 --fixed 180000 --units 1700` for
> contribution, then `roas --revenue 850000 --spend 240000 --cm-ratio 0.305`
> for contribution after ads, then subtract fixed costs. See the cost stack
> below — ৳347.5 of variable cost per order, not ৳260 of COGS.

```
Net Revenue      = 920,000 − 70,000            = ৳850,000
Gross Profit     = 850,000 − 442,000           = ৳408,000
Gross Margin     = 408,000 / 850,000           = 48.0%
AOV              = 850,000 / 1,700             = ৳500
```

**Full variable cost stack, per order:**

| Line | Per order | Monthly |
|---|---:|---:|
| Net selling price | ৳500 | ৳850,000 |
| − Product cost (COGS) | ৳260 | ৳442,000 |
| − Payment gateway 2.5% | ৳12 | ৳21,250 |
| − Shipping | ৳60 | ৳102,000 |
| − Packaging | ৳15 | ৳25,500 |
| **= CM before ads** | **৳153** | **৳259,250** (30.5%) |
| − Ad cost per order | ৳141 | ৳240,000 |
| **= CM after ads** | **৳11** | **৳19,250** (2.3%) |

```
Break-even ROAS = 1 / 0.305                    = 3.28x
Actual blended MER = 850,000 / 240,000         = 3.54x
Operating Profit = 19,250 − 180,000            = −৳160,750
```

### Step 5 — Diagnose
**Pattern D — High ROAS, weak profit**, sliding toward Pattern B.

The 48% gross margin is fine. It is also irrelevant. Once payment fees,
shipping and packaging come out, contribution margin before ads is **30.5%**,
which sets break-even ROAS at **3.28x**. The store is running at 3.54x. That
0.26x of headroom is the entire business — **৳11 of contribution per order.**

Covering ৳180,000 of fixed cost at a 30.5% contribution margin takes
**৳590,000 of net revenue** — the store does ৳850,000, so revenue is not the
problem. Ads are: after ad spend the ৳259,250 of contribution falls to
**৳19,250**, against ৳180,000 of fixed cost. The gap is
**৳160,750 lost every month.**

### Step 6 — Sensitivity
Ad cost is the dominant variable. At 3.28x ROAS, contribution goes to zero.
At 3.0x it is negative — meaning a routine CPM increase of ~15% makes every
order actively loss-making.

Shipping is the second lever: ৳102,000/month, 12% of net revenue.

### Step 7 — Recommend

**IMMEDIATE (this week)**
1. Stop scaling spend. Cut the lowest-ROAS ad sets below 3.28x — they are
   subsidised losses. → protects roughly ৳40–60k · effort: low
2. Add a free-shipping threshold at ৳800. Shipping is 12% of revenue and AOV is
   ৳500. → target +15% AOV · effort: low

**NEXT 30 DAYS**
1. Raise price 8–10%. At 30.5% CM, a 10% rise tolerates 24.7% volume loss
   before contribution falls. → potential +৳70k/month · effort: low
2. Renegotiate courier rate at 1,700 orders/month volume. ৳10/order saved =
   ৳17,000/month. · effort: medium
3. Cut fixed costs. ৳180,000 against ৳259,250 of pre-ad contribution is too
   heavy for this revenue level. · effort: medium

**NEXT 90 DAYS**
1. Build repeat purchase — the second order carries no CAC, so it converts at
   30.5% contribution instead of 2.3%. Email/SMS flows to existing buyers.
2. Reduce ad dependency. 100% of revenue is paid-acquired; that is the
   structural problem, not the ROAS.

### Final verdict
Not profitable — losing **৳160,750/month**. Cash-flow negative. Growth is
value-destructive: every additional order at current economics contributes ৳11
against ৳106 of fixed cost per order. **Biggest problem: fixed costs are sized
for a business roughly 3× this one, and ad efficiency has no margin of safety.**
Fix price and shipping first; they are the fastest levers.

---

## Example 2 — "We made ৳420k profit but the bank account went down"

### Input
Net profit ৳420,000 · depreciation ৳35,000 · AR increased ৳380,000 · inventory
increased ৳250,000 · AP increased ৳90,000 · capex ৳120,000 · loan principal
repaid ৳150,000 · owner drawings ৳200,000. Monthly COGS ৳1,800,000, revenue
৳2,600,000. Avg inventory ৳900,000, avg AR ৳1,450,000, avg AP ৳520,000.

### Calculate

```
Operating Cash Flow = 420,000 + 35,000 − 380,000 − 250,000 + 90,000
                    = −৳85,000

Net cash change     = −85,000 − 120,000 (capex)
                              − 150,000 (loan principal)
                              − 200,000 (drawings)
                    = −৳555,000
```

**Cash conversion cycle (30-day period):**
```
DIO = 900,000 / 1,800,000 × 30   = 15.0 days
DSO = 1,450,000 / 2,600,000 × 30 = 16.7 days
DPO = 520,000 / 1,800,000 × 30   =  8.7 days
CCC = 15.0 + 16.7 − 8.7          = 23.1 days
```

### Diagnose
**Pattern C — Profitable on paper, cash poor.**

The ৳420,000 profit is real. It is just not in cash. ৳630,000 went into
receivables and inventory. Below the profit line, another ৳470,000 left for
capex, loan principal and drawings — **none of which appear on the P&L.**

Loan principal repayment is the most commonly missed item: interest is an
expense, principal is not. It still consumes cash.

### Recommend

**IMMEDIATE**
1. Pause owner drawings until operating cash flow turns positive.
   → ৳200,000/month · effort: low (but requires a decision)
2. Chase the AR increase. Every 10 days of DSO removed releases roughly
   **৳866,667** at current revenue. · effort: low

**NEXT 30 DAYS**
1. Halt inventory build. ৳250,000 went into stock this month against 15 days
   of cover — that is above requirement. · effort: low
2. Extend supplier terms. DPO of 8.7 days is unusually short; moving to 21 days
   releases roughly ৳738,000 of working capital. · effort: medium

**NEXT 90 DAYS**
1. Introduce advance/partial payment terms for new customers.
2. Re-plan capex against actual operating cash flow, not profit.

### Final verdict
Profitable, but **cash-flow negative by ৳555,000**. Growth is consuming more
working capital than it generates. **Biggest problem: the business is financing
its customers** — 23-day cash cycle with only 8.7 days of supplier credit.
Nothing here requires more sales; it requires collecting faster and buying less.

---

## Example 3 — "Should I raise prices? I'll lose customers."

### Input
Price ৳1,200 · variable cost ৳720 · volume 1,000 units/month · proposed +10%.

### Calculate

```
CM per unit now  = 1,200 − 720                = ৳480   (40% CM ratio)
Total CM now     = 480 × 1,000                = ৳480,000

At +10%:
New price        = ৳1,320
New CM per unit  = 1,320 − 720                = ৳600
Units needed to hold contribution = 480,000 / 600 = 800 units

Max tolerable volume loss = 10% / (40% + 10%) = 20.0%
```

### Diagnose
The founder can lose **200 of 1,000 customers — a full 20%** — and still make
the same total contribution. Below a 20% loss, the price rise increases profit.

At a 10% volume loss (900 units): CM = 900 × 600 = **৳540,000**, up ৳60,000/month
on 100 fewer orders — which also means lower fulfilment, support and shipping
cost. The gain is understated.

### Recommend
Test, don't guess:
1. Raise price on **one SKU or one channel** for 30 days. Measure actual volume
   change against the 20% threshold.
2. Pair the increase with an added-value element (faster delivery, bundle,
   guarantee) so it reads as repositioning, not a hike.
3. Grandfather existing repeat customers for one cycle to protect retention.

### Final verdict
The arithmetic strongly favours the increase — the break-even volume loss of
20% is far above what a 10% price change typically produces. **Do not confuse
fear of losing customers with the economics of losing them.** Test on a
segment, then roll out.

---

*Worked examples — skill by **Md Kamrul Hasan** ·
https://github.com/Kamrul5242*
