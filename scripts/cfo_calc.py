#!/usr/bin/env python3
"""
cfo_calc.py — deterministic finance calculator for the
Entrepreneur Business Intelligence & CFO skill.

Standard library only. No installs. Python 3.8+.

Usage:
    python3 cfo_calc.py <command> [--flags]
    python3 cfo_calc.py list
    python3 cfo_calc.py margins --revenue 850000 --cogs 442000 --opex 180000
    python3 cfo_calc.py unit --price 500 --varcost 347 --fixed 180000
    python3 cfo_calc.py cac --spend 240000 --customers 1700 --ltv 900
    python3 cfo_calc.py roas --revenue 850000 --spend 240000 --cm-ratio 0.305
    python3 cfo_calc.py runway --cash 1200000 --burn 160750
    python3 cfo_calc.py ccc --inventory 900000 --ar 1450000 --ap 520000 \
                            --cogs 1800000 --revenue 2600000 --days 30
    python3 cfo_calc.py npv --rate 0.15 --initial 500000 --flows 150000,200000,250000,300000
    python3 cfo_calc.py loan --principal 1000000 --annual-rate 0.14 --months 36
    python3 cfo_calc.py dilution --pre 50000000 --investment 10000000 --founder 100
    python3 cfo_calc.py price-test --price 1200 --varcost 720 --units 1000 --increase 0.10

Author: Md Kamrul Hasan
GitHub: https://github.com/Kamrul5242
License: MIT
"""

import argparse
import json
import sys

SIG = "Md Kamrul Hasan | github.com/Kamrul5242 | MKH-EBIC-2.1.0"


# ---------- helpers ----------

def _div(a, b):
    """Safe division. Returns None instead of raising."""
    try:
        if b in (0, None):
            return None
        return a / b
    except (TypeError, ZeroDivisionError):
        return None


def _pct(x, nd=1):
    return None if x is None else round(x * 100, nd)


def _r(x, nd=2):
    return None if x is None else round(x, nd)


def _flows(s):
    return [float(x.strip()) for x in s.split(",") if x.strip()]


# ---------- commands ----------

def margins(a):
    net_rev = a.revenue - (a.returns or 0)
    gp = net_rev - a.cogs
    op = gp - (a.opex or 0)
    ebitda = op + (a.depreciation or 0) + (a.amortization or 0)
    ebt = op - (a.interest or 0)
    net = ebt - (a.tax or 0)
    return {
        "gross_revenue": _r(a.revenue),
        "returns": _r(a.returns or 0),
        "net_revenue": _r(net_rev),
        "cogs": _r(a.cogs),
        "gross_profit": _r(gp),
        "gross_margin_pct": _pct(_div(gp, net_rev)),
        "operating_expenses": _r(a.opex or 0),
        "operating_profit_ebit": _r(op),
        "operating_margin_pct": _pct(_div(op, net_rev)),
        "ebitda": _r(ebitda),
        "ebitda_margin_pct": _pct(_div(ebitda, net_rev)),
        "pre_tax_profit": _r(ebt),
        "net_profit": _r(net),
        "net_margin_pct": _pct(_div(net, net_rev)),
        "note": "All margins use NET revenue as denominator.",
    }


def unit(a):
    cm = a.price - a.varcost
    cm_ratio = _div(cm, a.price)
    bep_units = _div(a.fixed, cm) if a.fixed else None
    bep_rev = _div(a.fixed, cm_ratio) if (a.fixed and cm_ratio) else None
    out = {
        "price": _r(a.price),
        "variable_cost": _r(a.varcost),
        "contribution_margin_per_unit": _r(cm),
        "cm_ratio_pct": _pct(cm_ratio),
        "break_even_units": None if bep_units is None else round(bep_units, 1),
        "break_even_revenue": _r(bep_rev),
        "break_even_roas": _r(_div(1, cm_ratio)),
    }
    if a.units:
        total_cm = cm * a.units
        out["units"] = a.units
        out["total_contribution"] = _r(total_cm)
        out["operating_profit"] = _r(total_cm - (a.fixed or 0))
        if bep_units:
            out["margin_of_safety_pct"] = _pct(_div(a.units - bep_units, a.units))
    if a.target_profit:
        out["units_for_target_profit"] = round(
            _div((a.fixed or 0) + a.target_profit, cm), 1)
    if cm <= 0:
        out["ALERT"] = "Contribution margin is zero or negative. Every sale loses money."
    return out


def cac(a):
    c = _div(a.spend, a.customers)
    out = {
        "acquisition_spend": _r(a.spend),
        "new_customers": a.customers,
        "cac": _r(c),
    }
    if a.ltv:
        out["ltv"] = _r(a.ltv)
        out["ltv_cac_ratio"] = _r(_div(a.ltv, c))
    if a.monthly_contribution:
        out["monthly_contribution_per_customer"] = _r(a.monthly_contribution)
        out["cac_payback_months"] = _r(_div(c, a.monthly_contribution))
    if a.arpu and a.gross_margin and a.lifetime:
        computed = a.arpu * a.gross_margin * a.lifetime
        out["ltv_computed"] = _r(computed)
        out["ltv_computed_note"] = "ARPU x gross margin (decimal) x lifetime, same period unit"
        out["ltv_cac_computed"] = _r(_div(computed, c))
    if a.churn:
        out["implied_lifetime_periods"] = _r(_div(1, a.churn))
    out["warning"] = "State whether CAC is paid, blended, or fully loaded."
    return out


def roas(a):
    r = _div(a.revenue, a.spend)
    out = {
        "attributed_revenue": _r(a.revenue),
        "ad_spend": _r(a.spend),
        "roas": _r(r),
    }
    if a.cm_ratio:
        be = _div(1, a.cm_ratio)
        out["cm_ratio_before_ads_pct"] = _pct(a.cm_ratio)
        out["break_even_roas"] = _r(be)
        out["headroom"] = _r(r - be) if (r and be) else None
        out["verdict"] = (
            "PROFITABLE on ads" if (r and be and r > be)
            else "LOSING MONEY on ads at this ROAS"
        )
        contribution = a.revenue * a.cm_ratio - a.spend
        out["contribution_after_ads"] = _r(contribution)
    if a.total_revenue:
        out["blended_mer"] = _r(_div(a.total_revenue, a.spend))
        out["mer_note"] = "If MER is far below platform ROAS, attribution is over-claiming."
    return out


def runway(a):
    months = _div(a.cash, a.burn)
    status = "unknown"
    if months is not None:
        if months < 3:
            status = "CRITICAL — survival mode"
        elif months < 6:
            status = "URGENT — raise or cut now"
        elif months < 12:
            status = "WATCH — plan the next move"
        else:
            status = "COMFORTABLE"
    return {
        "cash_available": _r(a.cash),
        "monthly_net_burn": _r(a.burn),
        "runway_months": _r(months),
        "status": status,
        "caveat": "Valid only if burn is stable. If burn is growing, forecast month by month.",
    }


def ccc(a):
    dio = _div(a.inventory, a.cogs)
    dso = _div(a.ar, a.revenue)
    dpo = _div(a.ap, a.cogs)
    dio = dio * a.days if dio is not None else None
    dso = dso * a.days if dso is not None else None
    dpo = dpo * a.days if dpo is not None else None
    cycle = None
    if None not in (dio, dso, dpo):
        cycle = dio + dso - dpo
    return {
        "days_in_period": a.days,
        "DIO_days": _r(dio, 1),
        "DSO_days": _r(dso, 1),
        "DPO_days": _r(dpo, 1),
        "cash_conversion_cycle_days": _r(cycle, 1),
        "daily_cogs": _r(_div(a.cogs, a.days)),
        "daily_revenue": _r(_div(a.revenue, a.days)),
        "cash_released_per_day_of_dso_improvement": _r(_div(a.revenue, a.days)),
        "reading": ("Negative CCC: customers fund operations."
                    if (cycle is not None and cycle < 0)
                    else "Positive CCC: cash is tied up between paying and collecting."),
    }


def npv(a):
    flows = _flows(a.flows)
    total = -a.initial
    schedule = []
    for t, cf in enumerate(flows, start=1):
        pv = cf / ((1 + a.rate) ** t)
        total += pv
        schedule.append({"period": t, "cash_flow": _r(cf), "present_value": _r(pv)})

    # IRR by bisection
    def _npv_at(rate):
        v = -a.initial
        for t, cf in enumerate(flows, start=1):
            v += cf / ((1 + rate) ** t)
        return v

    irr = None
    lo, hi = -0.9999, 10.0
    if _npv_at(lo) * _npv_at(hi) < 0:
        for _ in range(300):
            mid = (lo + hi) / 2
            if _npv_at(lo) * _npv_at(mid) <= 0:
                hi = mid
            else:
                lo = mid
        irr = (lo + hi) / 2

    # simple payback
    cum, payback = -a.initial, None
    for t, cf in enumerate(flows, start=1):
        prev = cum
        cum += cf
        if cum >= 0 and payback is None:
            payback = t - 1 + (-prev / cf if cf else 0)

    return {
        "discount_rate_pct": _pct(a.rate),
        "initial_investment": _r(a.initial),
        "schedule": schedule,
        "npv": _r(total),
        "irr_pct": _pct(irr) if irr is not None else "not solvable in range",
        "payback_periods": _r(payback),
        "verdict": ("Creates value at this discount rate" if total > 0
                    else "Destroys value at this discount rate"),
    }


def loan(a):
    r = a.annual_rate / 12
    n = a.months
    if r == 0:
        emi = a.principal / n
    else:
        emi = a.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    total = emi * n
    out = {
        "principal": _r(a.principal),
        "annual_rate_pct": _pct(a.annual_rate),
        "months": n,
        "monthly_emi": _r(emi),
        "total_repayment": _r(total),
        "total_interest": _r(total - a.principal),
        "interest_as_pct_of_principal": _pct(_div(total - a.principal, a.principal)),
    }
    if a.monthly_ocf:
        out["monthly_operating_cash_flow"] = _r(a.monthly_ocf)
        out["dscr"] = _r(_div(a.monthly_ocf, emi))
        out["dscr_reading"] = (
            "Below 1.0 — cannot service from operations" if _div(a.monthly_ocf, emi) < 1
            else "Above 1.0 — serviceable, check the conservative scenario too"
        )
    return out


def dilution(a):
    post = a.pre + a.investment
    inv_pct = _div(a.investment, post)
    return {
        "pre_money": _r(a.pre),
        "investment": _r(a.investment),
        "post_money": _r(post),
        "investor_ownership_pct": _pct(inv_pct),
        "dilution_pct": _pct(inv_pct),
        "founder_before_pct": _r(a.founder),
        "founder_after_pct": _r(a.founder * (1 - inv_pct)),
        "note": "If an option pool is created pre-money, founders absorb that dilution too.",
    }


def price_test(a):
    cm = a.price - a.varcost
    cm_ratio = _div(cm, a.price)
    new_price = a.price * (1 + a.increase)
    new_cm = new_price - a.varcost
    max_loss = _div(a.increase, cm_ratio + a.increase)
    units_needed = _div(cm * a.units, new_cm)
    return {
        "current_price": _r(a.price),
        "variable_cost": _r(a.varcost),
        "current_cm_per_unit": _r(cm),
        "current_cm_ratio_pct": _pct(cm_ratio),
        "current_units": a.units,
        "current_total_contribution": _r(cm * a.units),
        "price_increase_pct": _pct(a.increase),
        "new_price": _r(new_price),
        "new_cm_per_unit": _r(new_cm),
        "units_needed_to_break_even": _r(units_needed, 1),
        "max_tolerable_volume_loss_pct": _pct(max_loss),
        "reading": (
            "You can lose up to {}% of volume and still make the same "
            "contribution.".format(_pct(max_loss))
        ),
    }


COMMANDS = {
    "margins": "Full P&L: gross, operating, EBITDA, net margins",
    "unit": "Contribution margin, break-even units/revenue, margin of safety",
    "cac": "CAC, LTV, LTV:CAC, payback period",
    "roas": "ROAS vs break-even ROAS, blended MER, contribution after ads",
    "runway": "Cash runway in months with status",
    "ccc": "DIO, DSO, DPO, cash conversion cycle",
    "npv": "NPV, IRR, payback for an investment",
    "loan": "EMI, total interest, DSCR",
    "dilution": "Post-money, investor %, founder dilution",
    "price-test": "Break-even volume loss for a price change",
}


def build_parser():
    p = argparse.ArgumentParser(
        description="Deterministic CFO calculator. " + SIG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List all commands")

    m = sub.add_parser("margins", help=COMMANDS["margins"])
    m.add_argument("--revenue", type=float, required=True)
    m.add_argument("--returns", type=float, default=0)
    m.add_argument("--cogs", type=float, required=True)
    m.add_argument("--opex", type=float, default=0)
    m.add_argument("--depreciation", type=float, default=0)
    m.add_argument("--amortization", type=float, default=0)
    m.add_argument("--interest", type=float, default=0)
    m.add_argument("--tax", type=float, default=0)

    u = sub.add_parser("unit", help=COMMANDS["unit"])
    u.add_argument("--price", type=float, required=True)
    u.add_argument("--varcost", type=float, required=True)
    u.add_argument("--fixed", type=float, default=0)
    u.add_argument("--units", type=float)
    u.add_argument("--target-profit", type=float, dest="target_profit")

    c = sub.add_parser("cac", help=COMMANDS["cac"])
    c.add_argument("--spend", type=float, required=True)
    c.add_argument("--customers", type=float, required=True)
    c.add_argument("--ltv", type=float)
    c.add_argument("--monthly-contribution", type=float, dest="monthly_contribution")
    c.add_argument("--arpu", type=float)
    c.add_argument("--gross-margin", type=float, dest="gross_margin",
                   help="decimal, e.g. 0.45")
    c.add_argument("--lifetime", type=float, help="periods, same unit as ARPU")
    c.add_argument("--churn", type=float, help="decimal per period")

    r = sub.add_parser("roas", help=COMMANDS["roas"])
    r.add_argument("--revenue", type=float, required=True)
    r.add_argument("--spend", type=float, required=True)
    r.add_argument("--cm-ratio", type=float, dest="cm_ratio",
                   help="decimal CM ratio before ads, e.g. 0.305")
    r.add_argument("--total-revenue", type=float, dest="total_revenue")

    rw = sub.add_parser("runway", help=COMMANDS["runway"])
    rw.add_argument("--cash", type=float, required=True)
    rw.add_argument("--burn", type=float, required=True)

    cc = sub.add_parser("ccc", help=COMMANDS["ccc"])
    cc.add_argument("--inventory", type=float, required=True)
    cc.add_argument("--ar", type=float, required=True)
    cc.add_argument("--ap", type=float, required=True)
    cc.add_argument("--cogs", type=float, required=True)
    cc.add_argument("--revenue", type=float, required=True)
    cc.add_argument("--days", type=int, default=30)

    n = sub.add_parser("npv", help=COMMANDS["npv"])
    n.add_argument("--rate", type=float, required=True, help="decimal per period")
    n.add_argument("--initial", type=float, required=True)
    n.add_argument("--flows", type=str, required=True, help="comma-separated")

    l = sub.add_parser("loan", help=COMMANDS["loan"])
    l.add_argument("--principal", type=float, required=True)
    l.add_argument("--annual-rate", type=float, dest="annual_rate", required=True)
    l.add_argument("--months", type=int, required=True)
    l.add_argument("--monthly-ocf", type=float, dest="monthly_ocf")

    d = sub.add_parser("dilution", help=COMMANDS["dilution"])
    d.add_argument("--pre", type=float, required=True)
    d.add_argument("--investment", type=float, required=True)
    d.add_argument("--founder", type=float, default=100)

    pt = sub.add_parser("price-test", help=COMMANDS["price-test"])
    pt.add_argument("--price", type=float, required=True)
    pt.add_argument("--varcost", type=float, required=True)
    pt.add_argument("--units", type=float, default=1)
    pt.add_argument("--increase", type=float, required=True, help="decimal, e.g. 0.10")

    return p


DISPATCH = {
    "margins": margins, "unit": unit, "cac": cac, "roas": roas,
    "runway": runway, "ccc": ccc, "npv": npv, "loan": loan,
    "dilution": dilution, "price-test": price_test,
}


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.cmd or args.cmd == "list":
        print("cfo_calc.py — commands:\n")
        for k, v in COMMANDS.items():
            print("  {:<12} {}".format(k, v))
        print("\nRun: python3 cfo_calc.py <command> --help")
        print("\n" + SIG)
        return 0
    result = DISPATCH[args.cmd](args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
