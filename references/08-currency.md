# Currency Handling

**Default: BDT (৳).** Every currency below is fully supported. Switch the moment
the user signals a different one.

---

## 1. Detecting which currency to use

Priority order — first match wins:

1. **Explicit symbol or code in the user's message** — `$`, `€`, `£`, `USD`, `taka`, `rupee`
2. **Bengali number words** — "lakh", "crore", "hazar", "লাখ", "কোটি" → BDT
3. **Stated country or market** — "my store in Dubai" → AED
4. **Prior currency in this conversation** — stay consistent
5. **Nothing at all** → **BDT**, and say so once: *"Using BDT — tell me if it's a different currency."*

Never silently switch mid-analysis. If the user's data mixes currencies, stop
and flag it before computing anything.

---

## 2. Currency table

| Code | Symbol | Name | Decimals | Grouping |
|---|---|---|---|---|
| **BDT** | ৳ | Bangladeshi Taka | 2 | South Asian (lakh/crore) |
| INR | ₹ | Indian Rupee | 2 | South Asian |
| PKR | ₨ | Pakistani Rupee | 2 | South Asian |
| LKR | Rs | Sri Lankan Rupee | 2 | South Asian |
| NPR | रू | Nepalese Rupee | 2 | South Asian |
| USD | $ | US Dollar | 2 | Western (thousand/million) |
| EUR | € | Euro | 2 | Western |
| GBP | £ | Pound Sterling | 2 | Western |
| CAD | C$ | Canadian Dollar | 2 | Western |
| AUD | A$ | Australian Dollar | 2 | Western |
| AED | د.إ | UAE Dirham | 2 | Western |
| SAR | ﷼ | Saudi Riyal | 2 | Western |
| QAR | ﷼ | Qatari Riyal | 2 | Western |
| KWD | د.ك | Kuwaiti Dinar | **3** | Western |
| BHD | .د.ب | Bahraini Dinar | **3** | Western |
| OMR | ﷼ | Omani Rial | **3** | Western |
| MYR | RM | Malaysian Ringgit | 2 | Western |
| SGD | S$ | Singapore Dollar | 2 | Western |
| THB | ฿ | Thai Baht | 2 | Western |
| IDR | Rp | Indonesian Rupiah | **0** | Western |
| VND | ₫ | Vietnamese Dong | **0** | Western |
| PHP | ₱ | Philippine Peso | 2 | Western |
| CNY | ¥ | Chinese Yuan | 2 | Western |
| JPY | ¥ | Japanese Yen | **0** | Western |
| KRW | ₩ | Korean Won | **0** | Western |
| TRY | ₺ | Turkish Lira | 2 | Western |
| EGP | E£ | Egyptian Pound | 2 | Western |
| NGN | ₦ | Nigerian Naira | 2 | Western |
| ZAR | R | South African Rand | 2 | Western |
| KES | KSh | Kenyan Shilling | 2 | Western |
| BRL | R$ | Brazilian Real | 2 | Western |
| MXN | Mex$ | Mexican Peso | 2 | Western |
| CHF | CHF | Swiss Franc | 2 | Western |
| SEK | kr | Swedish Krona | 2 | Western |
| RUB | ₽ | Russian Ruble | 2 | Western |

Any currency not listed: use its ISO 4217 code as the prefix (`XOF 250,000`)
and 2 decimals unless the user says otherwise.

**Zero-decimal currencies (JPY, KRW, IDR, VND):** never show cents. `¥1,250`
not `¥1,250.00`.
**Three-decimal currencies (KWD, BHD, OMR):** `KWD 1.250`, not `KWD 1.25`.

---

## 3. South Asian grouping — BDT, INR, PKR, LKR, NPR

Use lakh and crore when the user does. This is how founders in these markets
actually think, and converting to millions makes the answer harder to read.

```
1 lakh   = 100,000        written 1,00,000
1 crore  = 10,000,000     written 1,00,00,000
```

Digit grouping is **2-2-3 from the right**, not 3-3-3:

| Value | South Asian | Western |
|---|---|---|
| 100,000 | ৳1,00,000 (1 lakh) | ৳100,000 |
| 850,000 | ৳8,50,000 (8.5 lakh) | ৳850,000 |
| 10,000,000 | ৳1,00,00,000 (1 crore) | ৳10,000,000 |

**In prose, name the scale:** "৳8.5 lakh" reads faster than "৳850,000".
**In tables, use plain digits** so columns align.

Mirror the user: if they write "5 lakh", answer in lakh. If they write
"500000", answer in plain digits.

---

## 4. Conversion rules

**Do not convert unless the user asks, or a current verified rate is available.**
A stale rate produces a confidently wrong number.

When converting, always show all four:

```
Original:   $12,000 USD
Rate:       1 USD = 121.50 BDT
Converted:  ৳14,58,000 BDT
Rate date:  2026-08-20 (source: <name>)
```

If no reliable current rate exists, say so and keep both currencies visible
side by side rather than guessing.

---

## 5. Multi-currency businesses

Common for exporters, importers, and freelancers — costs in one currency,
revenue in another.

**Rules:**
1. Compute margins in the **currency the cost is incurred in**, then present in
   the user's home currency.
2. Never sum mixed currencies into one total without conversion and a stated rate.
3. Report FX exposure explicitly: *"Revenue is 100% USD, costs are 80% BDT. A 5%
   BDT appreciation cuts gross margin by roughly 4 percentage points."*
4. Compute the **break-even exchange rate** — the rate at which the deal stops
   being profitable. This is the number an exporter actually needs.

```
Break-even FX rate = Total Cost (local currency) / Revenue (foreign currency)
```

Example: costs ৳9,72,000, revenue $10,000 → break-even rate is 97.2 BDT/USD.
Above that rate the deal profits; below it, it loses.

---

## 6. Formatting rules

- Symbol before the number, no space: `৳850,000` · `$1,200` · `€450`
- Where a symbol is ambiguous (¥ = CNY or JPY; ₨ = PKR or LKR; ﷼ = SAR/QAR/OMR),
  use the ISO code: `JPY 1,250`
- Negatives in parentheses in tables: `(৳1,60,750)`
- Zero renders as `–` in financial tables, not `৳0`
- Percentages 1 decimal: `30.5%`
- Ratios and multiples: `3.28x`
- **Never mix currencies inside one table column.**
- **Every money figure carries its symbol.** A bare number in a financial
  report is a defect.

---

*Currency reference — skill by **Md Kamrul Hasan** · https://github.com/Kamrul5242*
