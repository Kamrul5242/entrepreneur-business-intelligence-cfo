# E-commerce, POD, Marketplace and Inventory

The general formula library assumes a clean business. Physical-goods and
online-retail businesses have cost layers that quietly destroy margin and are
almost always missing from the founder's own math.

---

## 1. The real cost stack per order

Build this before believing any margin number.

```
Selling price (what the customer pays)
− Discount / coupon actually applied
= Net selling price
− Product cost (LANDED, not invoice)
− Inbound freight, duty, clearing (if not already in landed)
− Packaging and inserts
− Pick, pack, handling labour
− Outbound shipping (your share)
− Payment gateway fee (% + fixed)
− Marketplace / platform commission
− Ad cost allocated per order  (Ad spend / Orders)
− Refund & return provision     (Refund rate × net price)
− RTO provision                 (RTO rate × round-trip shipping cost)
− Chargeback / fraud provision
────────────────────────────────
= CONTRIBUTION MARGIN PER ORDER
```

**Only this number tells you whether to scale.** Gross margin will look fine
while the business loses money on every sale.

---

## 2. The costs founders forget

| Hidden cost | Why it's missed |
|---|---|
| **RTO / COD failure** | Order counted as a sale, then returned; two-way shipping paid, product may be damaged |
| **Landed cost vs invoice cost** | Freight, duty, clearing, and inbound handling silently added to COGS |
| **Free shipping** | Not free — it's a discount taken out of margin |
| **Return processing labour** | Inspecting, repacking, restocking, or writing off |
| **Dead stock** | Cash sitting on a shelf, often never expensed until written off |
| **Payment gateway fixed fee** | Brutal on low AOV — ৳5 fixed on a ৳200 order is 2.5% |
| **Sample and defect loss** | Especially apparel: yield loss, shade variation, sizing rejects |
| **Ad creative production** | Photography, models, editing — real acquisition cost |
| **Currency loss** | Buying in USD, selling in BDT, with a lag |
| **Platform fee changes** | Marketplace commission is not fixed forever |

---

## 3. Print-on-demand specifics

POD trades margin for zero inventory risk. The analysis must reflect that trade.

```
POD contribution = Retail price
                 − Base/production cost
                 − Shipping (or shipping subsidy)
                 − Marketplace fee (e.g. listing + transaction + payment)
                 − Ad cost per order
                 − Refund provision
```

Notes:
- **Gross margin 20–40% is normal.** Do not diagnose it as broken.
- The real levers are: AOV (bundles, multi-item orders), organic vs paid mix,
  and design win-rate — not cost reduction.
- Design portfolio economics: most designs earn nothing. Measure
  **revenue per published design** and **% of designs with ≥1 sale**, then
  judge whether the production effort is worth it.
- Zero inventory means **near-zero working capital tied up** — which makes a
  thin margin far more tolerable than the same margin in a stocked business.
- Platform dependency is the dominant risk. Model the "account suspended"
  scenario explicitly.

---

## 4. Pre-order model economics

Pre-order is a cash-flow instrument disguised as a sales channel.

```
Cash collected up front       ৳ A   (customer money, before production)
Production cost to fulfil     ৳ B   (paid after collection)
Pre-order funding benefit     = A − B  available during the production window
```

Analysis must cover:
- **Negative cash conversion cycle** — customer funds production. This is the
  whole point; quantify it.
- **Fulfilment risk** — a missed delivery date converts prepaid revenue into a
  refund liability. Model refund exposure as a real liability, not a footnote.
- **Break-even order count** before committing to a production run (MOQ).
- **Deposit vs full payment** — deposit lowers customer risk and conversion
  friction but reduces the funding benefit.
- **Unearned revenue is a liability, not profit.** Do not report pre-order cash
  as revenue until delivery.

```
Pre-order break-even units = (Fixed production setup + MOQ commitment)
                             / Contribution margin per unit
```

---

## 5. Apparel / B2B sourcing specifics

- **Quote the full landed cost**: FOB + freight + insurance + duty + clearing +
  inland transport + inspection. Buyers compare landed, not FOB.
- **Yield loss**: fabric consumption vs usable output. A 5% yield loss on a 20%
  margin removes a quarter of the profit.
- **Payment terms drive the cash cycle**: LC at sight vs 60/90-day terms changes
  DSO more than any operational improvement.
- **Order concentration** is the standard failure mode — one buyer, one season.
- **Sample cost** and development cost are real acquisition costs; allocate them
  to CAC, not to overhead.
- **Currency exposure**: costs often in local currency, revenue in USD/EUR.
  Quantify the exposure and the rate at which the deal turns unprofitable.

---

## 6. Marketplace vs own-store comparison

| Dimension | Marketplace | Own store |
|---|---|---|
| CAC | Low / built-in traffic | High / paid |
| Commission | 5–20% of revenue | 0 |
| Payment fee | Bundled | 2–3% |
| Customer data | Usually not owned | Owned |
| Repeat / LTV | Weak, platform owns relationship | Strong |
| Platform risk | High — suspension ends the business | Low |
| Margin per order | Lower | Higher |

**Correct comparison:** contribution margin per order **including CAC** on each
channel, plus LTV difference from owning the customer relationship. Marketplaces
usually win on first order and lose on the fifth.

---

## 7. Metrics to compute for any e-commerce business

```
AOV                  = Net Revenue / Orders
Units per order      = Units Sold / Orders
Contribution / order = (from §1 stack)
Break-even ROAS      = 1 / CM ratio before ads
MER                  = Total Revenue / Total Marketing Spend
Repeat rate          = Customers with ≥2 orders / Total customers
Refund rate          = Refunded orders / Total orders
RTO rate             = RTO orders / Shipped orders
Inventory turnover   = COGS / Average inventory
Sell-through         = Units sold / Units received
GMROI                = Gross profit / Average inventory cost
Dead stock value     = Zero-movement units × landed cost
Cash tied in stock   = Inventory value at cost
```

---

## 8. Diagnostic questions specific to this sector

1. Is contribution margin after ads positive at current ROAS?
2. What is break-even ROAS, and how far is actual ROAS from it?
3. How much cash is trapped in inventory, and how many days of sales is it?
4. What share of SKUs generates 80% of gross profit? (Usually very few.)
5. What is the RTO/refund cost as a % of revenue?
6. Is AOV rising or falling — and is discounting the cause?
7. What % of revenue depends on a single platform or ad account?
8. If the ad account were disabled tomorrow, what revenue remains?

---

*E-commerce and inventory reference — skill by **Md Kamrul Hasan** ·
https://github.com/Kamrul5242*
