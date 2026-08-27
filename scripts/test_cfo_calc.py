#!/usr/bin/env python3
"""
test_cfo_calc.py — regression tests for the CFO calculator.

Standard library only (unittest). No installs.

    python3 scripts/test_cfo_calc.py

Every figure asserted here is independently derived in
references/06-worked-examples.md. If a test fails, either the calculator
changed behaviour or the worked example is wrong — check both.

Author: Md Kamrul Hasan
GitHub: https://github.com/Kamrul5242
License: MIT
Signature: MKH-EBIC-2.2.0
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cfo_calc  # noqa: E402


def run(argv):
    """Parse argv the way main() does and return the command's dict."""
    args = cfo_calc.build_parser().parse_args(argv)
    return cfo_calc.DISPATCH[args.cmd](args)


class ParserHealth(unittest.TestCase):
    """A bare % in an argparse help string raised ValueError on Python 3.13+
    while the parser was being built, killing every command."""

    def test_parser_builds(self):
        cfo_calc.build_parser()

    def test_every_command_help_renders(self):
        parser = cfo_calc.build_parser()
        parser.format_help()
        for action in parser._subparsers._group_actions[0].choices.values():
            action.format_help()

    def test_list_output_has_no_doubled_percent(self):
        # COMMANDS feeds both argparse and the plain-text `list` output.
        for text in cfo_calc.COMMANDS.values():
            self.assertNotIn("%%", text)

    def test_every_command_is_dispatchable(self):
        self.assertEqual(set(cfo_calc.COMMANDS), set(cfo_calc.DISPATCH))


class WorkedExample1(unittest.TestCase):
    """'ROAS 3.5x, why am I broke?' — truth is a LOSS of 160,750."""

    TRUTH = -160750.0

    def test_margins_full_cost_stack(self):
        r = run(["margins", "--revenue", "850000", "--cogs", "442000",
                 "--variable", "148750", "--adspend", "240000",
                 "--opex", "180000"])
        self.assertEqual(r["contribution_after_variable"], 259250.0)
        self.assertEqual(r["contribution_margin_pct"], 30.5)
        self.assertEqual(r["net_profit"], self.TRUTH)
        self.assertNotIn("WARNING", r)

    def test_unit_agrees_with_margins(self):
        r = run(["unit", "--price", "500", "--varcost", "347.5",
                 "--fixed", "180000", "--units", "1700", "--adspend", "240000"])
        self.assertEqual(r["total_contribution_before_ads"], 259250.0)
        self.assertEqual(r["total_contribution_after_ads"], 19250.0)
        self.assertEqual(r["operating_profit"], self.TRUTH)

    def test_ad_spend_removes_the_phantom_safety_margin(self):
        """Without ad spend the store looks 30.6% above break-even. It is not."""
        without = run(["unit", "--price", "500", "--varcost", "347.5",
                       "--fixed", "180000", "--units", "1700"])
        with_ads = run(["unit", "--price", "500", "--varcost", "347.5",
                        "--fixed", "180000", "--units", "1700",
                        "--adspend", "240000"])
        self.assertGreater(without["margin_of_safety_pct"], 0)
        self.assertLess(with_ads["margin_of_safety_pct"], 0)
        self.assertIn("operating_profit_before_ad_spend", without)
        self.assertNotIn("operating_profit", without)

    def test_roas_break_even(self):
        r = run(["roas", "--revenue", "850000", "--spend", "240000",
                 "--cm-ratio", "0.305"])
        self.assertEqual(r["break_even_roas"], 3.28)
        self.assertEqual(r["contribution_after_ads"], 19250.0)
        self.assertIn("before fixed costs", r["verdict"])

    def test_omitting_costs_warns(self):
        r = run(["margins", "--revenue", "850000", "--cogs", "442000",
                 "--opex", "180000"])
        self.assertIn("WARNING", r)


class WorkedExample2(unittest.TestCase):
    """'We made 420k profit but the bank account went down.'"""

    def test_cashflow(self):
        r = run(["cashflow", "--net-profit", "420000", "--depreciation", "35000",
                 "--delta-ar", "380000", "--delta-inventory", "250000",
                 "--delta-ap", "90000", "--capex", "120000",
                 "--loan-principal", "150000", "--drawings", "200000"])
        self.assertEqual(r["operating_cash_flow"], -85000.0)
        self.assertEqual(r["net_cash_change"], -555000.0)

    def test_ccc(self):
        r = run(["ccc", "--inventory", "900000", "--ar", "1450000",
                 "--ap", "520000", "--cogs", "1800000",
                 "--revenue", "2600000", "--days", "30"])
        self.assertEqual(r["DIO_days"], 15.0)
        self.assertEqual(r["DSO_days"], 16.7)
        self.assertEqual(r["DPO_days"], 8.7)
        self.assertEqual(r["cash_conversion_cycle_days"], 23.1)


class WorkedExample3(unittest.TestCase):
    """'Should I raise prices?'"""

    def test_price_test(self):
        r = run(["price-test", "--price", "1200", "--varcost", "720",
                 "--units", "1000", "--increase", "0.10"])
        self.assertEqual(r["new_cm_per_unit"], 600.0)
        self.assertEqual(r["units_needed_to_break_even"], 800.0)
        self.assertEqual(r["max_tolerable_volume_loss_pct"], 20.0)


class EdgeCases(unittest.TestCase):
    """Each of these crashed or lied in a previous revision."""

    def test_negative_burn_is_not_critical(self):
        r = run(["runway", "--cash", "1200000", "--burn", "-50000"])
        self.assertIsNone(r["runway_months"])
        self.assertNotIn("CRITICAL", r["status"])

    def test_positive_burn_still_graded(self):
        r = run(["runway", "--cash", "1200000", "--burn", "160750"])
        self.assertEqual(r["runway_months"], 7.47)
        self.assertIn("WATCH", r["status"])

    def test_zero_cm_target_profit_does_not_crash(self):
        r = run(["unit", "--price", "100", "--varcost", "100",
                 "--target-profit", "1000"])
        self.assertIsNone(r["units_for_target_profit"])
        self.assertIsNone(r["break_even_units"])
        self.assertIn("ALERT", r)

    def test_negative_cm_still_reports_ad_spend(self):
        r = run(["unit", "--price", "100", "--varcost", "120",
                 "--units", "500", "--adspend", "10000"])
        self.assertEqual(r["ad_spend"], 10000.0)

    def test_exact_break_even_roas_is_not_a_loss(self):
        r = run(["roas", "--revenue", "1000", "--spend", "305",
                 "--cm-ratio", "0.305"])
        self.assertIn("BREAK-EVEN", r["verdict"])

    def test_zero_emi_dscr_does_not_crash(self):
        r = run(["loan", "--principal", "0", "--annual-rate", "0.14",
                 "--months", "36", "--monthly-ocf", "50000"])
        self.assertIsNone(r["dscr"])

    def test_explicit_zero_ad_spend_silences_warning(self):
        """0 is an answer; absence is not. They must not be conflated."""
        r = run(["margins", "--revenue", "100000", "--cogs", "40000",
                 "--variable", "5000", "--adspend", "0", "--opex", "20000"])
        self.assertNotIn("WARNING", r)

    def test_negative_closing_cash_alerts(self):
        r = run(["cashflow", "--net-profit", "-50000", "--delta-ar", "100000",
                 "--opening-cash", "20000"])
        self.assertEqual(r["closing_cash"], -130000.0)
        self.assertIn("ALERT", r)


class BusinessInvalidInputs(unittest.TestCase):
    """A finance tool must fail loudly rather than return tidy nonsense.
    Each of these crashed or produced a meaningless number before v2.2.0."""

    def test_discount_rate_of_minus_100_pct(self):
        r = run(["npv", "--rate", "-1", "--initial", "1000", "--flows", "100,200"])
        self.assertIn("ERROR", r)

    def test_loan_with_zero_term(self):
        r = run(["loan", "--principal", "100000", "--annual-rate", "0.12",
                 "--months", "0"])
        self.assertIn("ERROR", r)

    def test_dilution_with_zero_post_money(self):
        r = run(["dilution", "--pre", "0", "--investment", "0"])
        self.assertIn("ERROR", r)

    def test_price_test_with_zero_price(self):
        r = run(["price-test", "--price", "0", "--varcost", "10",
                 "--increase", "0.1"])
        self.assertIn("ERROR", r)

    def test_refunds_exceeding_sales_is_flagged(self):
        r = run(["margins", "--revenue", "100000", "--returns", "150000",
                 "--cogs", "40000", "--variable", "0", "--adspend", "0"])
        self.assertIn("ALERT", r)

    def test_zero_revenue_is_flagged_not_divided_by(self):
        r = run(["margins", "--revenue", "0", "--cogs", "0",
                 "--variable", "0", "--adspend", "0"])
        self.assertIn("ALERT", r)
        self.assertIsNone(r["gross_margin_pct"])

    def test_zero_customers_does_not_divide_by_zero(self):
        r = run(["cac", "--spend", "1000", "--customers", "0"])
        self.assertIsNone(r["cac"])

    def test_zero_ad_spend_roas(self):
        r = run(["roas", "--revenue", "1000", "--spend", "0", "--cm-ratio", "0.3"])
        self.assertIsNone(r["roas"])

    def test_negative_cash_runway(self):
        r = run(["runway", "--cash", "-50000", "--burn", "1000"])
        self.assertLess(r["runway_months"], 0)

    def test_ccc_with_zero_cogs(self):
        r = run(["ccc", "--inventory", "1000", "--ar", "1000", "--ap", "1000",
                 "--cogs", "0", "--revenue", "0"])
        self.assertIsNone(r["DIO_days"])

    def test_inventory_with_no_usable_input(self):
        r = run(["inventory"])
        self.assertIn("ERROR", r)

    def test_zero_price_unit_alerts(self):
        r = run(["unit", "--price", "0", "--varcost", "50", "--fixed", "1000"])
        self.assertIn("ALERT", r)


class IntakeSheet(unittest.TestCase):
    """The intake command must reproduce the worked example from the CSV."""

    def test_example_csv_reproduces_worked_example(self):
        here = os.path.dirname(os.path.abspath(__file__))
        csv = os.path.join(here, "..", "assets", "business-data-intake-example.csv")
        if not os.path.exists(csv):
            self.skipTest("example intake sheet not present")
        r = run(["intake", "--file", csv])
        pl = r["profit_and_loss"]
        self.assertEqual(pl["net_revenue"], 850000.0)
        self.assertEqual(pl["contribution"], 259250.0)
        self.assertEqual(pl["operating_profit"], -160750.0)
        self.assertEqual(r["unit_economics"]["break_even_roas"], 3.28)
        self.assertEqual(r["cash"]["unexplained_gap"], 0.0)
        self.assertEqual(r["balance_sheet_check"]["difference"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
