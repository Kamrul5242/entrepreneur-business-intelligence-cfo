#!/usr/bin/env python3
"""
pl_model.py — the canonical profit-and-loss definition for this skill.

THIS FILE IS THE SOURCE OF TRUTH.

Everything that states the P&L must agree with what is defined here:

    scripts/cfo_calc.py                 imports BRIDGE and computes with it
    assets/cfo-premium-dashboard.xlsx   mirrors it in Excel formulas
    references/01-formula-library.md    documents it for the model to read
    platforms/*                         restate it for other hosts
    references/06-worked-examples.md    demonstrates it

`scripts/test_reference_consistency.py` parses the reference documentation and
evaluates it against this module numerically, so prose that drifts away from
the implementation fails a test rather than silently teaching the wrong model.

WHY THIS EXISTS
  The same P&L was written out independently in nine places. It drifted three
  times: `margins` and `intake` disagreed on depreciation (v2.2.1), the
  platform adapters disagreed with the calculator, and the formula library
  still taught the pre-v2.2.0 chain that omitted per-order variable costs -
  the model that once reported +228,000 for a business losing 160,750.

THE ONE RULE THAT PREVENTS DOUBLE COUNTING
  Every cost belongs to EXACTLY ONE bucket. There is no "treat it as direct if
  you prefer" option. Payment processing is a VARIABLE cost, never COGS.
  Packaging is COGS, never VARIABLE. Ad spend and D&A are broken out of
  operating expenses so that FIXED_OPEX never contains them.

Author: Md Kamrul Hasan
GitHub: https://github.com/Kamrul5242
License: MIT
Signature: MKH-EBIC-2.2.5
"""

# --------------------------------------------------------------------------
# Cost classification. Each line item appears in exactly one bucket; the test
# suite asserts that invariant, and asserts the intake template agrees.
# --------------------------------------------------------------------------

BUCKETS = {
    "COGS": {
        "csv_section": "COGS",
        "description": "Cost of goods sold, at LANDED cost. Above gross profit.",
        "items": [
            "Product / Material Cost",
            "Inbound Freight",
            "Duty & Clearing",
            "Direct Labour",
            "Packaging",
        ],
    },
    "VARIABLE": {
        "csv_section": "VARIABLE",
        "description": ("Costs that scale with an order but sit below COGS. "
                        "The bucket founders forget."),
        "items": [
            "Outbound Shipping",
            "Payment Gateway Fees",
            "Marketplace Commission",
            "RTO / Failed Delivery Cost",
        ],
    },
    "AD_SPEND": {
        "csv_section": "OPEX",
        "description": ("Advertising, broken out of operating expenses because "
                        "break-even ROAS is measured against contribution."),
        "items": ["Advertising Spend"],
    },
    "FIXED_OPEX": {
        "csv_section": "OPEX",
        "description": ("Overhead that does not scale with an order. EXCLUDES "
                        "advertising and D&A, which are separate terms."),
        "items": [
            "Salaries (non-production)",
            "Owner Compensation",
            "Rent",
            "Software & Subscriptions",
            "Utilities",
            "Professional Fees",
            "Other Operating",
        ],
    },
    "DNA": {
        "csv_section": "OPEX",
        "description": ("Depreciation and amortization. An operating cost: it "
                        "is subtracted to reach operating profit and added "
                        "back to reach EBITDA. Unconditionally."),
        "items": ["Depreciation & Amortization"],
    },
    "BELOW_LINE": {
        "csv_section": "BELOW_LINE",
        "description": "Below the operating line.",
        "items": ["Interest Expense", "Tax"],
    },
}

# --------------------------------------------------------------------------
# The bridge. Machine-readable so documentation can be validated against it.
# Each step is (result, [(sign, term), ...]) where a term is an input name or
# the result of an earlier step.
# --------------------------------------------------------------------------

BRIDGE = [
    ("Net Revenue",      [("+", "Gross Revenue"), ("-", "Returns"),
                          ("-", "Discounts")]),
    ("Gross Profit",     [("+", "Net Revenue"), ("-", "COGS")]),
    ("Contribution",     [("+", "Gross Profit"), ("-", "Variable Costs")]),
    ("Operating Profit", [("+", "Contribution"), ("-", "Ad Spend"),
                          ("-", "Fixed OpEx"), ("-", "D&A")]),
    ("EBITDA",           [("+", "Operating Profit"), ("+", "D&A")]),
    ("Pre-tax Profit",   [("+", "Operating Profit"), ("-", "Interest")]),
    ("Net Profit",       [("+", "Pre-tax Profit"), ("-", "Tax")]),
]

INPUTS = ("Gross Revenue", "Returns", "Discounts", "COGS", "Variable Costs",
          "Ad Spend", "Fixed OpEx", "D&A", "Interest", "Tax")

# Margins are always taken on NET revenue, never gross.
MARGIN_DENOMINATOR = "Net Revenue"


def evaluate(**values):
    """Run the bridge. Keys are INPUTS names; missing inputs default to 0.

    Returns a dict keyed by every bridge result name.
    """
    env = {name: float(values.get(name, 0) or 0) for name in INPUTS}
    for result, terms in BRIDGE:
        total = 0.0
        for sign, term in terms:
            if term not in env:
                raise KeyError("bridge term %r is not an input or an earlier "
                               "result" % (term,))
            total += env[term] if sign == "+" else -env[term]
        env[result] = total
    return env


def bridge_text():
    """The bridge as the reference documentation should state it."""
    lines = []
    for result, terms in BRIDGE:
        expr = ""
        for i, (sign, term) in enumerate(terms):
            if i == 0:
                expr = term if sign == "+" else "-" + term
            else:
                expr += " %s %s" % ("+" if sign == "+" else "−", term)
        lines.append("%-18s = %s" % (result, expr))
    return "\n".join(lines)


def all_items():
    """Every classified line item, for the exactly-one-bucket invariant."""
    out = []
    for meta in BUCKETS.values():
        out.extend(meta["items"])
    return out


if __name__ == "__main__":
    print(__doc__.strip().split("\n")[2])
    print()
    print(bridge_text())
    print()
    for name, meta in BUCKETS.items():
        print("%-11s %s" % (name, ", ".join(meta["items"])))
