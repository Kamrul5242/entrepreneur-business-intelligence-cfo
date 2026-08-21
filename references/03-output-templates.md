# Output Templates

Pick the template that matches the request size. Do not use the full CFO report
for a one-line question.

---

## Template A — Quick Answer (default for a single question)

```
[Direct answer in one sentence, with the number.]

How I got there:
  <formula> = <substitution> = <result>

What it means: <one or two sentences>
Watch out for: <the one caveat that matters>
```

Use when the user asks one thing. Do not pad it into a report.

---

## Template B — Money In / Money Out

```
Cash In:        ৳ X
Cash Out:       ৳ Y
─────────────────────
Net Cash Flow:  ৳ Z

By type:  Operating ৳a  |  Investing ৳b  |  Financing ৳c

Biggest inflow:   <source> ৳
Biggest outflow:  <category> ৳  (n% of all outflow)

<One-line verdict.>
```

---

## Template C — Full CFO Report

### 1. Executive Summary
Lead with the verdict, not the data.

| Metric | Value | Period | Note |
|---|---|---|---|
| Net Revenue | | | |
| Gross Profit / Margin | | | |
| Contribution Margin | | | after all variable cost |
| Operating Profit | | | |
| Net Profit / Margin | | | |
| Cash In → Out → Net | | | |
| Runway | | | |
| CAC / LTV / Ratio | | | state which CAC |
| Break-even | | | units and revenue |

### 2. Data Quality
What was given, what was assumed, what is missing, what conflicted.

### 3. Financial Diagnosis
What is working. What is not. The pattern (A–H) this business matches.

### 4. Unit Economics
Does one order make money? Show the per-unit stack:
```
Price                 ৳
− COGS (landed)       ৳
− Payment fees        ৳
− Shipping            ৳
− Marketplace fee     ৳
− Ad cost per order   ৳
− Refund provision    ৳
────────────────────────
= Contribution / order ৳   (n% of price)
```

### 5. Cash Position
Cash In → Cash Out → Net Cash. Runway. Cash conversion cycle.

### 6. Growth Assessment
Is growth creating or destroying value? Show the evidence.

### 7. Scenarios
Conservative / Base / Aggressive across the key lines.

### 8. Risks
Top 3–5, each with: what · likelihood · ৳ impact · early signal · mitigation.

### 9. Recommended Actions
```
IMMEDIATE (this week)
  1. <action>  → expected impact ৳X  → effort: low/med/high

NEXT 30 DAYS
  1. <action>  → expected impact ৳X  → effort:

NEXT 90 DAYS
  1. <action>  → expected impact ৳X  → effort:
```

### 10. Final Verdict
Answer all five, plainly:
- Is the business profitable?
- Is it cash-flow healthy?
- Is growth sustainable?
- What is the single biggest problem?
- What should the founder do next?

---

## Template D — Investment / Deal Evaluation

```
The ask:          <amount, structure, terms>
Valuation:        pre ৳ / post ৳ / method used
Dilution:         founder before % → after %
Payback:          <periods>
NPV @ <rate>:     ৳        (state why that rate)
IRR:              %
Break-even:       <when the deal repays itself>

Upside case:   <assumptions → outcome>
Downside case: <assumptions → outcome>
Deal-breakers: <the terms that would make this a no>

Verdict: <take it / negotiate X / walk away> — because <the number>.
```

---

## Formatting rules

- Currency symbol on every money figure. Period label on every metric.
- Tables for comparisons; prose for causes and recommendations.
- Bold the numbers that drive the decision.
- Mark every assumed input with `(assumed)`.
- Never open with a summary of what the user just told you.
- Never close with "let me know if you'd like me to elaborate" — elaborate or stop.

---

*Output templates — skill by **Md Kamrul Hasan** ·
https://github.com/Kamrul5242*
