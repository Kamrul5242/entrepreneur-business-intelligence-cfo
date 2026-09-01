#!/usr/bin/env python3
"""
cfo_calc.py — deterministic finance calculator for the
Entrepreneur Business Intelligence & CFO skill.

Standard library only. No installs. Python 3.8+.

Usage:
    python3 cfo_calc.py <command> [--flags]
    python3 cfo_calc.py list
    python3 cfo_calc.py margins --revenue 850000 --cogs 442000 --variable 148750 \
                                --adspend 240000 --opex 180000
    python3 cfo_calc.py unit --price 500 --varcost 347.5 --fixed 180000 \
                             --units 1700 --adspend 240000
    python3 cfo_calc.py intake --file assets/business-data-intake-example.csv
    python3 cfo_calc.py inventory --cogs 1800000 --avg-inventory 900000 \
                                  --daily-demand 57 --lead-days 21 --demand-std 12
    python3 cfo_calc.py cashflow --net-profit 420000 --depreciation 35000 \
                                 --delta-ar 380000 --delta-inventory 250000 \
                                 --delta-ap 90000 --capex 120000 \
                                 --loan-principal 150000 --drawings 200000
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
import csv
import json
import math
import statistics
import sys

# The P&L bridge lives in exactly one place. Do not restate it here.
import pl_model

SIG = "Md Kamrul Hasan | github.com/Kamrul5242 | MKH-EBIC-2.2.6"


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
    var = a.variable or 0
    ads = a.adspend or 0
    dna = (a.depreciation or 0) + (a.amortization or 0)
    # Every figure below comes from pl_model.BRIDGE, the single canonical
    # definition. Nothing here re-derives the P&L.
    b = pl_model.evaluate(**{
        "Gross Revenue": a.revenue, "Returns": a.returns or 0, "Discounts": 0,
        "COGS": a.cogs, "Variable Costs": var, "Ad Spend": ads,
        "Fixed OpEx": a.opex or 0, "D&A": dna,
        "Interest": a.interest or 0, "Tax": a.tax or 0,
    })
    contribution = b["Contribution"]
    op = b["Operating Profit"]
    ebitda = b["EBITDA"]
    ebt = b["Pre-tax Profit"]
    net = b["Net Profit"]
    out = {
        "gross_revenue": _r(a.revenue),
        "returns": _r(a.returns or 0),
        "net_revenue": _r(net_rev),
        "cogs": _r(a.cogs),
        "gross_profit": _r(gp),
        "gross_margin_pct": _pct(_div(gp, net_rev)),
        "variable_costs": _r(var),
        "contribution_after_variable": _r(contribution),
        "contribution_margin_pct": _pct(_div(contribution, net_rev)),
        "ad_spend": _r(ads),
        "operating_expenses": _r(a.opex or 0),
        "depreciation_amortization": _r(dna),
        "operating_profit_ebit": _r(op),
        "operating_margin_pct": _pct(_div(op, net_rev)),
        "ebitda": _r(ebitda),
        "ebitda_margin_pct": _pct(_div(ebitda, net_rev)),
        "pre_tax_profit": _r(ebt),
        "net_profit": _r(net),
        "net_margin_pct": _pct(_div(net, net_rev)),
        "note": "All margins use NET revenue as denominator.",
    }
    # `is None` not falsiness: 0 is a real answer, absence is not.
    if net_rev <= 0:
        out["ALERT"] = (
            "Net revenue is zero or negative, so every margin percentage below "
            "is meaningless. Check returns and discounts against gross revenue.")
    omitted = [name for name, val in
               (("--variable (shipping, gateway, commission, RTO)", a.variable),
                ("--adspend", a.adspend)) if val is None]
    if omitted:
        out["WARNING"] = (
            "No value given for: " + "; ".join(omitted) +
            ". If this business has those costs, every profit line above is "
            "overstated. Ad spend belongs in --adspend, not --opex.")
    return out


def unit(a):
    cm = a.price - a.varcost
    cm_ratio = _div(cm, a.price)
    # A non-positive CM never recovers fixed cost: break-even is undefined,
    # not a negative number of units.
    bep_units = _div(a.fixed, cm) if (a.fixed and cm > 0) else None
    bep_rev = _div(a.fixed, cm_ratio) if (a.fixed and cm_ratio and cm > 0) else None
    out = {
        "price": _r(a.price),
        "variable_cost": _r(a.varcost),
        "contribution_margin_per_unit": _r(cm),
        "cm_ratio_pct": _pct(cm_ratio),
        "break_even_units": None if bep_units is None else round(bep_units, 1),
        "break_even_revenue": _r(bep_rev),
        "break_even_roas": _r(_div(1, cm_ratio)) if cm > 0 else None,
    }
    ads = getattr(a, "adspend", None) or 0
    bep_incl = None
    if ads:
        out["ad_spend"] = _r(ads)
        if cm > 0:
            # Ads are a period cost here, so they raise the bar the same way
            # fixed cost does. Break-even without them invents a safety margin.
            bep_incl = _div((a.fixed or 0) + ads, cm)
            out["break_even_units_incl_ad_spend"] = (
                None if bep_incl is None else round(bep_incl, 1))
    if a.units:
        total_cm = cm * a.units
        out["units"] = a.units
        out["total_contribution_before_ads"] = _r(total_cm)
        if ads:
            out["ad_cost_per_unit"] = _r(_div(ads, a.units))
            out["cm_per_unit_after_ads"] = _r(cm - (_div(ads, a.units) or 0))
            out["total_contribution_after_ads"] = _r(total_cm - ads)
            out["operating_profit"] = _r(total_cm - ads - (a.fixed or 0))
        else:
            # Naming the omission is the whole point: this number is not profit.
            out["operating_profit_before_ad_spend"] = _r(total_cm - (a.fixed or 0))
        gate = bep_incl if bep_incl is not None else bep_units
        if gate:
            out["margin_of_safety_pct"] = _pct(_div(a.units - gate, a.units))
            out["margin_of_safety_basis"] = (
                "break-even including ad spend" if bep_incl is not None
                else "break-even excluding ad spend — pass --adspend for the real figure")
    if a.target_profit:
        need = _div((a.fixed or 0) + a.target_profit, cm) if cm > 0 else None
        out["units_for_target_profit"] = (
            None if need is None else round(need, 1))
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
        if c == 0:
            out["ltv_cac_note"] = (
                "CAC is zero, so LTV:CAC is undefined rather than infinite. "
                "Either acquisition truly cost nothing this period, or the "
                "spend figure is missing.")
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
        # `if (r and be)` treated a ROAS of exactly 0 as missing, so a
        # campaign that returned nothing reported no headroom at all.
        out["headroom"] = (_r(r - be) if (r is not None and be is not None)
                           else None)
        if r is None or be is None:
            out["verdict"] = "not computable — need both ROAS and CM ratio"
        elif r > be:
            out["verdict"] = "PROFITABLE on ads (before fixed costs)"
        elif r == be:
            out["verdict"] = "BREAK-EVEN on ads — no contribution after ad cost"
        else:
            out["verdict"] = "LOSING MONEY on ads at this ROAS"
        contribution = a.revenue * a.cm_ratio - a.spend
        out["contribution_after_ads"] = _r(contribution)
        out["contribution_note"] = (
            "This is contribution AFTER ad spend but BEFORE fixed costs. "
            "Subtract rent, salaries and other overhead before calling it profit.")
    if a.total_revenue:
        out["blended_mer"] = _r(_div(a.total_revenue, a.spend))
        out["mer_note"] = "If MER is far below platform ROAS, attribution is over-claiming."
    return out


def runway(a):
    months = _div(a.cash, a.burn)
    status = "unknown"
    if a.burn is not None and a.burn <= 0:
        # Burn <= 0 means cash is not being consumed. Dividing cash by a
        # negative burn yields a negative "runway" that would otherwise be
        # graded CRITICAL, inverting the verdict for a healthy business.
        months = None
        if a.cash < 0:
            status = ("OVERDRAWN — the balance is negative. Cash is no longer "
                      "falling, but the hole still has to be filled"
                      if a.burn < 0 else
                      "OVERDRAWN — the balance is negative and flat")
        else:
            status = ("CASH POSITIVE — net cash is growing, runway is not limiting"
                      if a.burn < 0 else "NO NET BURN — cash is flat")
    elif months is not None:
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
    if a.rate <= -1:
        return {"ERROR": "Discount rate must be greater than -1 (-100%). "
                         "At -100% every future cash flow is worth nothing and "
                         "the present value is undefined.",
                "discount_rate_pct": _pct(a.rate)}
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
    if a.months <= 0:
        return {"ERROR": "Term must be at least one month.",
                "months": a.months}
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
        dscr = _div(a.monthly_ocf, emi)
        out["dscr"] = _r(dscr)
        out["dscr_reading"] = (
            "not computable — EMI is zero" if dscr is None
            else "Below 1.0 — cannot service from operations" if dscr < 1
            else "Above 1.0 — serviceable, check the conservative scenario too"
        )
    return out


# ---------- intake ----------

def _num(v):
    """CSV cells arrive as text, blank, or with thousands separators."""
    if v is None:
        return None
    t = str(v).strip().replace(",", "").replace("\u09f3", "").replace("$", "")
    if t in ("", "-", "n/a", "N/A"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


# Sections whose values are money. UNITS/MARKETING counts carry "count" in the
# currency column and must not be treated as a second currency.
_MONEY_SECTIONS = ("INCOME", "COGS", "VARIABLE", "OPEX", "BELOW_LINE",
                   "BALANCE", "CASH", "CONCENTRATION")
# Flow sections only. A balance sheet is a point in time, so its period
# legitimately differs from the P&L's.
_FLOW_SECTIONS = ("INCOME", "COGS", "VARIABLE", "OPEX", "BELOW_LINE")


def _load_intake(path):
    rows, meta = {}, {"currency": None, "period": None,
                      "currencies": {}, "periods": {}, "soft": []}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "section" not in reader.fieldnames:
            raise ValueError(
                "not an intake sheet: expected a 'section' column. Use "
                "assets/business-data-intake-template.csv as the format.")
        for r in reader:
            sec = (r.get("section") or "").strip().upper()
            item = (r.get("line_item") or "").strip().lower()
            if not sec or sec == "SIGNATURE":
                continue
            val = _num(r.get("value"))
            rows[(sec, item)] = val
            if val is None:
                continue
            cur = (r.get("currency") or "").strip()
            per = (r.get("period") or "").strip()
            # Hard rule 4: every number carries actual / estimated / assumed.
            conf = (r.get("confidence") or "").strip().lower()
            if conf and conf != "actual":
                meta["soft"].append("%s / %s (%s)" % (sec, item, conf))
            if sec in _MONEY_SECTIONS and cur and cur.lower() != "count":
                meta["currencies"].setdefault(cur.upper(), []).append(
                    "%s / %s" % (sec, item))
                if not meta["currency"]:
                    meta["currency"] = cur
            if sec in _FLOW_SECTIONS and per:
                meta["periods"].setdefault(" ".join(per.lower().split()), []).append(
                    "%s / %s" % (sec, item))
                if not meta["period"]:
                    meta["period"] = per
    return rows, meta


def _row(rows, section, needle):
    for (sec, item), val in rows.items():
        if sec == section and needle in item:
            return val
    return None


def _sec_sum(rows, section, exclude=()):
    total, seen = 0.0, False
    for (sec, item), val in rows.items():
        if sec != section or val is None:
            continue
        if any(x in item for x in exclude):
            continue
        total += val
        seen = True
    return total if seen else None


def intake(a):
    """Read a filled intake sheet and run the whole chain in one call."""
    rows, meta = _load_intake(a.file)
    missing = []

    def need(label, value):
        if value is None:
            missing.append(label)
        return value or 0.0

    # Summing two currencies into one number is meaningless, and this tool
    # deliberately does not invent an FX rate. Refuse rather than mislead.
    if len(meta["currencies"]) > 1:
        return {
            "ERROR": "This sheet mixes %d currencies (%s). Totals across "
                     "currencies are meaningless and no exchange rate is "
                     "assumed. Convert every money row to one currency at a "
                     "stated rate and date, then re-run."
                     % (len(meta["currencies"]), ", ".join(sorted(meta["currencies"]))),
            "currencies_found": {c: sorted(v) for c, v in
                                 sorted(meta["currencies"].items())},
            "source_file": a.file,
        }

    gross = _row(rows, "INCOME", "gross revenue")
    if gross is None:
        return {"ERROR": "INCOME / Gross Revenue is empty. Nothing can be "
                         "computed without it.", "file": a.file}

    returns = (_row(rows, "INCOME", "returns") or 0) + (_row(rows, "INCOME", "discount") or 0)
    cogs = _sec_sum(rows, "COGS") or 0.0
    var = _sec_sum(rows, "VARIABLE") or 0.0
    ads = _row(rows, "OPEX", "advertis") or 0.0
    dna = _row(rows, "OPEX", "depreciation") or 0.0
    opex = _sec_sum(rows, "OPEX", exclude=("advertis", "depreciation")) or 0.0
    interest = _row(rows, "BELOW_LINE", "interest") or 0.0
    tax = _row(rows, "BELOW_LINE", "tax") or 0.0

    # Same canonical bridge the `margins` command uses. When these two
    # disagreed on depreciation in v2.2.0 it was because each restated the
    # arithmetic separately; now neither does.
    b = pl_model.evaluate(**{
        "Gross Revenue": gross, "Returns": returns, "Discounts": 0,
        "COGS": cogs, "Variable Costs": var, "Ad Spend": ads,
        "Fixed OpEx": opex, "D&A": dna,
        "Interest": interest, "Tax": tax,
    })
    net_rev = b["Net Revenue"]
    gp = b["Gross Profit"]
    contribution = b["Contribution"]
    op = b["Operating Profit"]
    net = b["Net Profit"]

    pl = {
        "gross_revenue": _r(gross),
        "returns_and_discounts": _r(returns),
        "net_revenue": _r(net_rev),
        "cogs": _r(cogs),
        "gross_profit": _r(gp),
        "gross_margin_pct": _pct(_div(gp, net_rev)),
        "variable_costs": _r(var),
        "contribution": _r(contribution),
        "contribution_margin_pct": _pct(_div(contribution, net_rev)),
        "ad_spend": _r(ads),
        "operating_expenses": _r(opex),
        "depreciation_amortization": _r(dna),
        "operating_profit": _r(op),
        "operating_margin_pct": _pct(_div(op, net_rev)),
        "net_profit": _r(net),
        "net_margin_pct": _pct(_div(net, net_rev)),
    }

    out = {
        "source_file": a.file,
        "currency": meta["currency"] or "unknown",
        "period": meta["period"] or "unknown",
        "profit_and_loss": pl,
    }

    # ---- unit economics ----
    orders = _row(rows, "UNITS", "number of orders") or _row(rows, "UNITS", "units sold")
    if orders:
        cm_per_order = _div(contribution, orders)
        ue = {
            "orders": orders,
            "aov": _r(_div(net_rev, orders)),
            "variable_cost_per_order": _r(_div(cogs + var, orders)),
            "contribution_per_order": _r(cm_per_order),
            "ad_cost_per_order": _r(_div(ads, orders)),
            "contribution_after_ads_per_order": _r(
                (cm_per_order or 0) - (_div(ads, orders) or 0)),
            "fixed_cost_per_order": _r(_div(opex + dna, orders)),
        }
        cmr = _div(contribution, net_rev)
        if cmr and cmr > 0:
            ue["break_even_roas"] = _r(_div(1, cmr))
            ue["break_even_units_incl_ad_spend"] = _r(
                _div(opex + dna + ads, cm_per_order), 1)
        out["unit_economics"] = ue
        new_cust = _row(rows, "UNITS", "new customers")
        if new_cust:
            out["acquisition"] = {
                "new_customers": new_cust,
                "cac": _r(_div(ads, new_cust)),
                "contribution_per_order": _r(cm_per_order),
                "cac_note": "Paid CAC: ad spend / new customers. Not fully loaded.",
            }
    else:
        missing.append("UNITS / Number of Orders (unit economics skipped)")

    # ---- marketing ----
    attributed = _row(rows, "MARKETING", "ad-attributed")
    if attributed and ads:
        out["marketing"] = {
            "attributed_revenue": _r(attributed),
            "reported_roas": _r(_div(attributed, ads)),
            "blended_mer": _r(_div(net_rev, ads)),
        }

    # ---- cash ----
    opening = _row(rows, "CASH", "opening cash")
    closing = _row(rows, "CASH", "closing cash")
    capex = _row(rows, "CASH", "capital expenditure") or 0.0
    principal = _row(rows, "CASH", "principal repaid") or 0.0
    draw = _row(rows, "CASH", "drawings") or 0.0
    loan_in = _row(rows, "CASH", "loan received") or 0.0
    inv_in = _row(rows, "CASH", "investment received") or 0.0
    if opening is not None:
        implied = opening + op + dna - interest - tax + loan_in + inv_in - capex - principal - draw
        cash = {
            "opening_cash": _r(opening),
            "operating_profit": _r(op),
            "add_back_depreciation": _r(dna),
            "financing_in": _r(loan_in + inv_in),
            "less_capex": _r(capex),
            "less_loan_principal": _r(principal),
            "less_owner_drawings": _r(draw),
            "implied_closing_cash": _r(implied),
        }
        if closing is not None:
            gap = closing - implied
            cash["stated_closing_cash"] = _r(closing)
            cash["unexplained_gap"] = _r(gap)
            cash["gap_reading"] = (
                "Reconciles." if abs(gap) < 1 else
                "Does not reconcile. The difference is working-capital movement "
                "(receivables, inventory, payables) or a missing line. Run "
                "`cashflow` with the balance-sheet changes to locate it.")
        out["cash"] = cash

    # ---- working capital ----
    ar = _row(rows, "BALANCE", "receivable")
    inv = _row(rows, "BALANCE", "inventory")
    ap = _row(rows, "BALANCE", "payable")
    if None not in (ar, inv, ap) and cogs and net_rev:
        days = a.days
        dio = _div(inv, cogs) * days
        dso = _div(ar, net_rev) * days
        dpo = _div(ap, cogs) * days
        out["working_capital"] = {
            "days_in_period": days,
            "DIO_days": _r(dio, 1),
            "DSO_days": _r(dso, 1),
            "DPO_days": _r(dpo, 1),
            "cash_conversion_cycle_days": _r(dio + dso - dpo, 1),
        }

    # ---- balance sheet tie-out ----
    assets = _sec_sum(rows, "BALANCE", exclude=("payable", "debt", "equity"))
    liabilities = (_row(rows, "BALANCE", "payable") or 0) + \
                  (_row(rows, "BALANCE", "short-term debt") or 0) + \
                  (_row(rows, "BALANCE", "long-term debt") or 0)
    equity = _row(rows, "BALANCE", "equity")
    if assets is not None and equity is not None:
        diff = assets - (liabilities + equity)
        out["balance_sheet_check"] = {
            "assets": _r(assets),
            "liabilities": _r(liabilities),
            "equity": _r(equity),
            "difference": _r(diff),
            "reading": ("Balances." if abs(diff) < 1 else
                        "Does NOT balance. Assets minus liabilities and equity "
                        "leaves a gap — one of the three is wrong."),
        }

    # ---- concentration ----
    big_cust = _row(rows, "CONCENTRATION", "largest customer")
    if big_cust and net_rev:
        share = _div(big_cust, net_rev)
        out["concentration"] = {
            "largest_customer_share_pct": _pct(share),
            "flag": "ABOVE 20% — customer concentration risk" if share > 0.20
                    else "below the 20% flag",
        }

    # ---- the five answers SKILL.md section 5 requires ----
    # Runway answers "how long do we survive from here", so it must start
    # from cash on hand at the END of the period. Using the opening balance
    # overstates survival by the whole period's burn.
    runway_m = None
    cash_now = closing if closing is not None else opening
    runway_basis = ("closing cash" if closing is not None
                    else "opening cash - no closing balance given"
                    if opening is not None else None)
    if cash_now is not None and op < 0:
        runway_m = _div(cash_now, -op)
    cm_per_order_after_ads = None
    if orders:
        cm_per_order_after_ads = (_div(contribution, orders) or 0) - (_div(ads, orders) or 0)

    if contribution <= 0:
        problem = ("Unit economics. Contribution is not positive before ads — "
                   "every order loses money and volume makes it worse.")
    elif cm_per_order_after_ads is not None and cm_per_order_after_ads <= 0:
        problem = ("Ad efficiency. Contribution after ad cost is not positive, "
                   "so paid growth destroys value at this ROAS.")
    elif op < 0:
        problem = ("Fixed costs. Orders contribute after ads, but overhead of "
                   "{:,.0f} is larger than the {:,.0f} they produce."
                   .format(opex + dna, contribution - ads))
    elif runway_m is not None and runway_m < 3:
        problem = "Cash. Under three months of runway at the current burn."
    else:
        problem = "No structural loss detected in this period's numbers."

    out["minimum_viable_answer"] = {
        "profitable": "NO — operating loss" if op < 0 else "yes, at operating level",
        "operating_profit": _r(op),
        "does_one_unit_make_money": (
            "not computable without orders" if cm_per_order_after_ads is None
            else ("yes, {:,.2f} per order after ads".format(cm_per_order_after_ads)
                  if cm_per_order_after_ads > 0
                  else "NO, {:,.2f} per order after ads".format(cm_per_order_after_ads))),
        "runway_months": _r(runway_m),
        "runway_basis": runway_basis,
        "runway_cash_used": _r(cash_now),
        "biggest_problem": problem,
    }

    if len(meta["periods"]) > 1:
        out["ALERT"] = (
            "Income-statement rows span %d different periods (%s). Figures "
            "from different periods must not be added. Normalise every flow "
            "row to one period before trusting any total above."
            % (len(meta["periods"]), ", ".join(sorted(meta["periods"]))))
        out["periods_found"] = {p: sorted(v) for p, v in
                                sorted(meta["periods"].items())}
    if meta["soft"]:
        out["estimated_inputs"] = sorted(meta["soft"])
        out["estimated_inputs_note"] = (
            "%d input(s) are not marked 'actual'. Label every figure derived "
            "from them as estimated when reporting." % len(meta["soft"]))
    if missing:
        out["missing_inputs"] = missing
    out["note"] = ("Every figure derives from the sheet; nothing is assumed. "
                   "Blank rows are treated as zero and listed in missing_inputs "
                   "when they change the answer.")
    return out



def inventory(a):
    """Stock efficiency and reordering. Formulas per 05-ecommerce-and-inventory.md."""
    out = {}
    used = False

    if a.avg_inventory:
        out["average_inventory_at_cost"] = _r(a.avg_inventory)
        out["cash_tied_in_stock"] = _r(a.avg_inventory)
        if a.cogs:
            turns = _div(a.cogs, a.avg_inventory)
            out["inventory_turnover"] = _r(turns)
            out["days_of_stock"] = _r(_div(a.days, turns), 1)
            out["turnover_note"] = (
                "Turnover is per the period given by --days ({} days). "
                "Annualise before comparing to a yearly benchmark."
                .format(a.days))
            used = True
        if a.gross_profit:
            out["gmroi"] = _r(_div(a.gross_profit, a.avg_inventory))
            out["gmroi_note"] = ("Gross profit per unit of stock cost. Below 1.0 "
                                 "means the stock earns less than it costs to hold.")
            used = True

    if a.units_sold and a.units_received:
        out["sell_through_pct"] = _pct(_div(a.units_sold, a.units_received))
        used = True

    if a.dead_units and a.landed_cost:
        out["dead_stock_value"] = _r(a.dead_units * a.landed_cost)
        out["dead_stock_note"] = ("Zero-movement units at landed cost. This is "
                                  "cash already spent that no longer converts.")
        used = True

    # ---- reordering ----
    if a.daily_demand and a.lead_days:
        z = None
        if a.demand_std:
            try:
                z = statistics.NormalDist().inv_cdf(a.service_level)
            except Exception:
                z = None
        if z is not None:
            safety = z * a.demand_std * math.sqrt(a.lead_days)
        elif a.peak_daily_demand:
            safety = (a.peak_daily_demand - a.daily_demand) * a.lead_days
        else:
            safety = 0.0
        rop = a.daily_demand * a.lead_days + safety
        out["daily_demand_units"] = _r(a.daily_demand)
        out["lead_time_days"] = _r(a.lead_days)
        out["demand_during_lead_time"] = _r(a.daily_demand * a.lead_days, 1)
        out["safety_stock_units"] = _r(safety, 1)
        out["reorder_point_units"] = _r(rop, 1)
        out["safety_stock_basis"] = (
            "service level {:.0%}, z={:.2f}, sigma={:g}/day".format(
                a.service_level, z, a.demand_std) if z is not None
            else ("peak minus average demand over lead time"
                  if a.peak_daily_demand else
                  "ZERO — no --demand-std or --peak-daily-demand given, so this "
                  "reorder point carries no buffer against demand variability"))
        if a.stock_on_hand is not None:
            out["stock_on_hand"] = _r(a.stock_on_hand)
            out["reorder_now"] = a.stock_on_hand <= rop
            out["days_until_reorder_point"] = _r(
                _div(a.stock_on_hand - rop, a.daily_demand), 1)
        used = True

    if a.annual_demand and a.order_cost and a.holding_cost:
        eoq = math.sqrt(2 * a.annual_demand * a.order_cost / a.holding_cost)
        out["economic_order_quantity"] = _r(eoq, 1)
        out["orders_per_year"] = _r(_div(a.annual_demand, eoq), 1)
        out["eoq_note"] = ("EOQ assumes steady demand and a fixed order cost. "
                           "Treat it as a starting quantity, not a rule.")
        used = True

    if a.stockout_days and a.daily_demand and a.contribution_per_unit:
        lost = a.stockout_days * a.daily_demand * a.contribution_per_unit
        out["stockout_days"] = _r(a.stockout_days)
        out["contribution_lost_to_stockouts"] = _r(lost)
        used = True

    if not used:
        return {"ERROR": "Nothing to compute. Supply at least one group: "
                         "--cogs with --avg-inventory, --units-sold with "
                         "--units-received, --daily-demand with --lead-days, "
                         "or --annual-demand with --order-cost and --holding-cost."}
    return out



def cashflow(a):
    """Indirect-method cash flow: why profit and bank balance disagree."""
    dna = (a.depreciation or 0) + (a.amortization or 0)
    ocf = (a.net_profit + dna
           - (a.delta_ar or 0)
           - (a.delta_inventory or 0)
           + (a.delta_ap or 0)
           + (a.other_operating or 0))
    investing = -(a.capex or 0) + (a.asset_sales or 0)
    financing = (-(a.loan_principal or 0) - (a.drawings or 0)
                 + (a.new_financing or 0))
    net_change = ocf + investing + financing
    out = {
        "net_profit": _r(a.net_profit),
        "add_back_depreciation_amortization": _r(dna),
        "less_increase_in_receivables": _r(a.delta_ar or 0),
        "less_increase_in_inventory": _r(a.delta_inventory or 0),
        "add_increase_in_payables": _r(a.delta_ap or 0),
        "operating_cash_flow": _r(ocf),
        "less_capex": _r(a.capex or 0),
        "investing_cash_flow": _r(investing),
        "less_loan_principal_repaid": _r(a.loan_principal or 0),
        "less_owner_drawings": _r(a.drawings or 0),
        "financing_cash_flow": _r(financing),
        "net_cash_change": _r(net_change),
        "profit_to_cash_gap": _r(net_change - a.net_profit),
    }
    if a.opening_cash is not None:
        closing = a.opening_cash + net_change
        out["opening_cash"] = _r(a.opening_cash)
        out["closing_cash"] = _r(closing)
        if closing < 0:
            out["ALERT"] = "Closing cash is negative. This period cannot be funded."
    if ocf < 0 and a.net_profit > 0:
        out["reading"] = ("Profitable on paper, cash negative from operations. "
                          "Working capital is absorbing the profit.")
    elif net_change < 0 and a.net_profit > 0:
        out["reading"] = ("Profit is real but below-the-line items (capex, loan "
                          "principal, drawings) consumed more than it produced. "
                          "Principal repayment is not an expense but does spend cash.")
    elif ocf > 0:
        out["reading"] = "Operations generate cash."
    else:
        out["reading"] = "Operations consume cash."
    out["note"] = ("Indirect method. Unpaid invoices are not cash in; owner "
                   "drawings are cash out.")
    return out


def dilution(a):
    post = a.pre + a.investment
    inv_pct = _div(a.investment, post)
    if inv_pct is None:
        return {"ERROR": "Post-money valuation is zero or undefined, so "
                         "ownership percentages cannot be computed.",
                "pre_money": _r(a.pre), "investment": _r(a.investment),
                "post_money": _r(post)}
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
    if cm_ratio is None:
        return {"ERROR": "Price must be greater than zero to compute a "
                         "contribution-margin ratio.",
                "price": _r(a.price), "variable_cost": _r(a.varcost)}
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
    "cashflow": "Operating/investing/financing cash flow, profit-to-cash gap",
    "intake": "Read a filled intake CSV and run the whole chain in one call",
    "inventory": "Turnover, sell-through, GMROI, reorder point, EOQ, stockout cost",
    "dilution": "Post-money, investor %, founder dilution",
    "price-test": "Break-even volume loss for a price change",
}


def _h(key):
    """argparse %-expands help strings, so a literal % must be doubled."""
    return COMMANDS[key].replace("%", "%%")


def build_parser():
    p = argparse.ArgumentParser(
        description="Deterministic CFO calculator. " + SIG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List all commands")

    m = sub.add_parser("margins", help=_h("margins"))
    m.add_argument("--revenue", type=float, required=True)
    m.add_argument("--returns", type=float, default=0)
    m.add_argument("--cogs", type=float, required=True)
    m.add_argument("--variable", type=float,
                   help="costs that scale per order below COGS: outbound "
                        "shipping, payment gateway, marketplace commission, RTO. "
                        "Pass 0 explicitly to confirm there are none")
    m.add_argument("--adspend", type=float,
                   help="advertising spend for the period (do NOT also put it "
                        "in --opex). Pass 0 explicitly to confirm there is none")
    m.add_argument("--opex", type=float, default=0,
                   help="fixed overhead EXCLUDING depreciation and amortization: "
                        "rent, salaries, software, utilities. Pass D&A through "
                        "--depreciation / --amortization, which are subtracted "
                        "from operating profit and added back for EBITDA")
    m.add_argument("--depreciation", type=float, default=0)
    m.add_argument("--amortization", type=float, default=0)
    m.add_argument("--interest", type=float, default=0)
    m.add_argument("--tax", type=float, default=0)

    u = sub.add_parser("unit", help=_h("unit"))
    u.add_argument("--price", type=float, required=True)
    u.add_argument("--varcost", type=float, required=True)
    u.add_argument("--fixed", type=float, default=0)
    u.add_argument("--units", type=float)
    u.add_argument("--adspend", type=float,
                   help="total ad spend for the period covered by --units")
    u.add_argument("--target-profit", type=float, dest="target_profit")

    c = sub.add_parser("cac", help=_h("cac"))
    c.add_argument("--spend", type=float, required=True)
    c.add_argument("--customers", type=float, required=True)
    c.add_argument("--ltv", type=float)
    c.add_argument("--monthly-contribution", type=float, dest="monthly_contribution")
    c.add_argument("--arpu", type=float)
    c.add_argument("--gross-margin", type=float, dest="gross_margin",
                   help="decimal, e.g. 0.45")
    c.add_argument("--lifetime", type=float, help="periods, same unit as ARPU")
    c.add_argument("--churn", type=float, help="decimal per period")

    r = sub.add_parser("roas", help=_h("roas"))
    r.add_argument("--revenue", type=float, required=True)
    r.add_argument("--spend", type=float, required=True)
    r.add_argument("--cm-ratio", type=float, dest="cm_ratio",
                   help="decimal CM ratio before ads, e.g. 0.305")
    r.add_argument("--total-revenue", type=float, dest="total_revenue")

    rw = sub.add_parser("runway", help=_h("runway"))
    rw.add_argument("--cash", type=float, required=True)
    rw.add_argument("--burn", type=float, required=True)

    cc = sub.add_parser("ccc", help=_h("ccc"))
    cc.add_argument("--inventory", type=float, required=True)
    cc.add_argument("--ar", type=float, required=True)
    cc.add_argument("--ap", type=float, required=True)
    cc.add_argument("--cogs", type=float, required=True)
    cc.add_argument("--revenue", type=float, required=True)
    cc.add_argument("--days", type=int, default=30)

    n = sub.add_parser("npv", help=_h("npv"))
    n.add_argument("--rate", type=float, required=True, help="decimal per period")
    n.add_argument("--initial", type=float, required=True)
    n.add_argument("--flows", type=str, required=True, help="comma-separated")

    l = sub.add_parser("loan", help=_h("loan"))
    l.add_argument("--principal", type=float, required=True)
    l.add_argument("--annual-rate", type=float, dest="annual_rate", required=True,
                   help="decimal, e.g. 0.14 for 14%% per year")
    l.add_argument("--months", type=int, required=True)
    l.add_argument("--monthly-ocf", type=float, dest="monthly_ocf")

    ik = sub.add_parser("intake", help=_h("intake"))
    ik.add_argument("--file", "-f", required=True,
                    help="a filled copy of assets/business-data-intake-template.csv")
    ik.add_argument("--days", type=int, default=30,
                    help="days in the period, for DIO/DSO/DPO")

    iv = sub.add_parser("inventory", help=_h("inventory"))
    iv.add_argument("--cogs", type=float)
    iv.add_argument("--avg-inventory", type=float, dest="avg_inventory")
    iv.add_argument("--gross-profit", type=float, dest="gross_profit")
    iv.add_argument("--days", type=int, default=365,
                    help="days the --cogs figure covers (default 365)")
    iv.add_argument("--units-sold", type=float, dest="units_sold")
    iv.add_argument("--units-received", type=float, dest="units_received")
    iv.add_argument("--dead-units", type=float, dest="dead_units")
    iv.add_argument("--landed-cost", type=float, dest="landed_cost")
    iv.add_argument("--daily-demand", type=float, dest="daily_demand")
    iv.add_argument("--peak-daily-demand", type=float, dest="peak_daily_demand")
    iv.add_argument("--demand-std", type=float, dest="demand_std",
                    help="standard deviation of daily demand, in units")
    iv.add_argument("--service-level", type=float, dest="service_level",
                    default=0.95, help="decimal, e.g. 0.95 (default)")
    iv.add_argument("--lead-days", type=float, dest="lead_days")
    iv.add_argument("--stock-on-hand", type=float, dest="stock_on_hand")
    iv.add_argument("--annual-demand", type=float, dest="annual_demand")
    iv.add_argument("--order-cost", type=float, dest="order_cost")
    iv.add_argument("--holding-cost", type=float, dest="holding_cost",
                    help="cost to hold one unit for a year")
    iv.add_argument("--stockout-days", type=float, dest="stockout_days")
    iv.add_argument("--contribution-per-unit", type=float, dest="contribution_per_unit")

    cf = sub.add_parser("cashflow", help=_h("cashflow"))
    cf.add_argument("--net-profit", type=float, dest="net_profit", required=True)
    cf.add_argument("--depreciation", type=float, default=0)
    cf.add_argument("--amortization", type=float, default=0)
    cf.add_argument("--delta-ar", type=float, dest="delta_ar", default=0,
                    help="INCREASE in receivables (negative if it fell)")
    cf.add_argument("--delta-inventory", type=float, dest="delta_inventory", default=0,
                    help="INCREASE in inventory (negative if it fell)")
    cf.add_argument("--delta-ap", type=float, dest="delta_ap", default=0,
                    help="INCREASE in payables (negative if it fell)")
    cf.add_argument("--other-operating", type=float, dest="other_operating", default=0)
    cf.add_argument("--capex", type=float, default=0)
    cf.add_argument("--asset-sales", type=float, dest="asset_sales", default=0)
    cf.add_argument("--loan-principal", type=float, dest="loan_principal", default=0,
                    help="principal repaid — spends cash, is not an expense")
    cf.add_argument("--drawings", type=float, default=0)
    cf.add_argument("--new-financing", type=float, dest="new_financing", default=0,
                    help="loans received or equity injected")
    cf.add_argument("--opening-cash", type=float, dest="opening_cash")

    d = sub.add_parser("dilution", help=_h("dilution"))
    d.add_argument("--pre", type=float, required=True)
    d.add_argument("--investment", type=float, required=True)
    d.add_argument("--founder", type=float, default=100)

    pt = sub.add_parser("price-test", help=_h("price-test"))
    pt.add_argument("--price", type=float, required=True)
    pt.add_argument("--varcost", type=float, required=True)
    pt.add_argument("--units", type=float, default=1)
    pt.add_argument("--increase", type=float, required=True, help="decimal, e.g. 0.10")

    return p


DISPATCH = {
    "margins": margins, "unit": unit, "cac": cac, "roas": roas,
    "runway": runway, "ccc": ccc, "npv": npv, "loan": loan,
    "cashflow": cashflow, "intake": intake, "inventory": inventory,
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
