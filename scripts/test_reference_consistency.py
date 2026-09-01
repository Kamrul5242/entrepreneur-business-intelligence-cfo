#!/usr/bin/env python3
"""
test_reference_consistency.py — stop the documentation drifting from the code.

The same P&L is stated in the calculator, the workbook, the formula reference,
seven platform adapters and the worked examples. It has drifted three times.
`scripts/pl_model.py` is now the single definition; these tests prove every
other statement of it still agrees.

They are SEMANTIC, not prose matching. The bridge printed in
`references/01-formula-library.md` is parsed and EVALUATED on random inputs
against `pl_model`. Rewording is free; changing the arithmetic is not.

    python3 scripts/test_reference_consistency.py

Author: Md Kamrul Hasan
GitHub: https://github.com/Kamrul5242
License: MIT
Signature: MKH-EBIC-2.2.5
"""

import io
import os
import random
import re
import shlex
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pl_model  # noqa: E402

REFERENCE = os.path.join(ROOT, "references", "01-formula-library.md")
MINUS = "−"


def read(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def block(text, name):
    m = re.search(r"<!-- %s:start -->(.*?)<!-- %s:end -->" % (name, name),
                  text, re.S)
    if not m:
        raise AssertionError("marker block %r not found in the reference" % name)
    return m.group(1)


def parse_bridge(text):
    """Parse `Result = A − B + C` lines into pl_model's BRIDGE shape."""
    steps = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("```") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        terms, sign = [], "+"
        token = ""
        for ch in right:
            if ch in (MINUS, "+"):
                if token.strip():
                    terms.append((sign, token.strip()))
                sign = "-" if ch == MINUS else "+"
                token = ""
            else:
                token += ch
        if token.strip():
            terms.append((sign, token.strip()))
        steps.append((left.strip(), terms))
    return steps


def parse_buckets(text):
    """Parse the classification table into {TERM: [items]}."""
    out = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "Line items" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        term = cells[0].strip("`")
        items = [i.strip() for i in cells[2].split(",") if i.strip()]
        out[term] = items
    return out


def evaluate_steps(steps, values):
    env = dict(values)
    for result, terms in steps:
        total = 0.0
        for sign, term in terms:
            if term not in env:
                raise AssertionError(
                    "the reference uses term %r, which is neither an input nor "
                    "an earlier result. The documented chain is broken." % term)
            total += env[term] if sign == "+" else -env[term]
        env[result] = total
    return env


def random_inputs(seed):
    rnd = random.Random(seed)
    return {name: round(rnd.uniform(-50000, 500000), 2) for name in pl_model.INPUTS}


class CanonicalModel(unittest.TestCase):
    """Invariants of the source of truth itself."""

    def test_every_cost_belongs_to_exactly_one_bucket(self):
        """A cost in two buckets is subtracted twice."""
        items = pl_model.all_items()
        dupes = sorted({i for i in items if items.count(i) > 1})
        self.assertEqual(dupes, [], "line item(s) in more than one bucket: %r" % dupes)

    def test_every_bridge_term_resolves(self):
        pl_model.evaluate(**random_inputs(1))

    def test_bridge_uses_every_declared_input(self):
        used = {t for _, terms in pl_model.BRIDGE for _, t in terms}
        unused = sorted(set(pl_model.INPUTS) - used)
        self.assertEqual(unused, [], "declared input(s) never used: %r" % unused)


class ReferenceMatchesModel(unittest.TestCase):
    """The formula reference must compute what the code computes."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(REFERENCE):
            raise unittest.SkipTest("formula reference not present")
        cls.text = read(REFERENCE)

    def test_documented_bridge_evaluates_identically(self):
        steps = parse_bridge(block(self.text, "canonical-bridge"))
        self.assertTrue(steps, "no bridge lines parsed from the reference")
        for seed in range(25):
            values = random_inputs(seed)
            doc = evaluate_steps(steps, dict(values))
            code = pl_model.evaluate(**values)
            for result, _ in pl_model.BRIDGE:
                self.assertIn(result, doc,
                              "the reference does not define %r" % result)
                self.assertAlmostEqual(
                    doc[result], code[result], 6,
                    "reference and pl_model disagree on %r (seed %d)"
                    % (result, seed))

    def test_documented_buckets_match_the_model(self):
        doc = parse_buckets(block(self.text, "canonical-buckets"))
        code = {k: v["items"] for k, v in pl_model.BUCKETS.items()}
        self.assertEqual(sorted(doc), sorted(code),
                         "bucket names differ between reference and pl_model")
        for term in code:
            self.assertEqual(
                doc[term], code[term],
                "bucket %r differs: reference %r vs pl_model %r"
                % (term, doc[term], code[term]))

    def test_obsolete_conditional_dna_wording_is_gone(self):
        """The pre-v2.2.2 escape hatch that let D&A sit outside operating cost."""
        for phrase in ("only correct when D&A is included",
                       "EBITDA\n= Operating Profit, and you must say so"):
            self.assertNotIn(phrase, self.text,
                             "obsolete D&A wording is back: %r" % phrase)

    def test_reference_does_not_teach_the_simplified_chain(self):
        """`Operating Profit = Gross Profit - Operating Expenses` skips the
        variable bucket and ad spend, which is the model that once reported a
        profit for a loss-making business."""
        self.assertNotIn("Operating Profit    = Gross Profit %s Operating Expenses" % MINUS,
                         self.text)


class CalculatorMatchesModel(unittest.TestCase):
    """`margins` must be the bridge, not a second implementation of it."""

    def test_margins_equals_the_canonical_bridge(self):
        import cfo_calc
        for seed in range(15):
            v = random_inputs(seed)
            args = cfo_calc.build_parser().parse_args([
                "margins",
                "--revenue", str(v["Gross Revenue"]),
                "--returns", str(v["Returns"]),
                "--cogs", str(v["COGS"]),
                "--variable", str(v["Variable Costs"]),
                "--adspend", str(v["Ad Spend"]),
                "--opex", str(v["Fixed OpEx"]),
                "--depreciation", str(v["D&A"]),
                "--interest", str(v["Interest"]),
                "--tax", str(v["Tax"]),
            ])
            out = cfo_calc.margins(args)
            exp = pl_model.evaluate(**dict(v, **{"Discounts": 0}))
            for key, term in (("net_revenue", "Net Revenue"),
                              ("gross_profit", "Gross Profit"),
                              ("contribution_after_variable", "Contribution"),
                              ("operating_profit_ebit", "Operating Profit"),
                              ("ebitda", "EBITDA"),
                              ("pre_tax_profit", "Pre-tax Profit"),
                              ("net_profit", "Net Profit")):
                self.assertAlmostEqual(
                    out[key], round(exp[term], 2), 2,
                    "margins %r disagrees with the canonical %r (seed %d)"
                    % (key, term, seed))


class IntakeTemplateMatchesModel(unittest.TestCase):
    """The intake sheet is how founders classify costs; it must agree."""

    def test_template_sections_match_the_buckets(self):
        import csv as _csv
        path = os.path.join(ROOT, "assets", "business-data-intake-template.csv")
        if not os.path.exists(path):
            self.skipTest("intake template not present")
        by_section = {}
        with io.open(path, encoding="utf-8-sig", newline="") as fh:
            for row in _csv.DictReader(fh):
                by_section.setdefault(row["section"].strip().upper(), []).append(
                    row["line_item"].strip())
        for term in ("COGS", "VARIABLE"):
            self.assertEqual(
                by_section.get(term, []), pl_model.BUCKETS[term]["items"],
                "intake template section %r does not match pl_model" % term)
        opex = by_section.get("OPEX", [])
        expected = (pl_model.BUCKETS["AD_SPEND"]["items"]
                    + pl_model.BUCKETS["FIXED_OPEX"]["items"]
                    + pl_model.BUCKETS["DNA"]["items"])
        self.assertEqual(sorted(opex), sorted(expected),
                         "intake OPEX rows do not match ad spend + fixed opex + D&A")


class PlatformAdaptersMatchModel(unittest.TestCase):
    """All seven adapters restate the chain for other hosts."""

    def test_every_adapter_subtracts_the_same_four_terms(self):
        pdir = os.path.join(ROOT, "platforms")
        if not os.path.isdir(pdir):
            self.skipTest("platforms not present")
        expected = {"ad spend", "fixed opex", "d&a"}
        checked = 0
        for fn in sorted(os.listdir(pdir)):
            lines = read(os.path.join(pdir, fn)).split("\n")
            for i, line in enumerate(lines):
                # the definition line, not the "eight confusions" prose line
                if "=" not in line or "Contribution" not in line:
                    continue
                if "EBIT" not in line and "Operating Profit" not in line:
                    continue
                # plain-text adapters wrap the formula onto a second line
                rhs = line.split("=", 1)[1]
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if nxt.strip().lower().startswith(("minus", MINUS)):
                    rhs += " " + nxt
                rhs = (rhs.lower()
                       .replace(" minus ", " %s " % MINUS)
                       .replace("depreciation and amortization", "d&a")
                       .replace("depreciation + amortization", "d&a"))
                subtracted = {re.sub(r"\s+", " ", t).strip()
                              for t in rhs.split(MINUS)[1:] if t.strip()}
                missing = expected - subtracted
                self.assertEqual(
                    missing, set(),
                    "%s states operating profit without subtracting %r (parsed %r)"
                    % (fn, sorted(missing), sorted(subtracted)))
                checked += 1
                break
        self.assertGreaterEqual(checked, 6,
                                "expected an EBIT line in each adapter, found %d"
                                % checked)


class DocumentedCommandsRun(unittest.TestCase):
    """Every calculator example in the docs must run, and must not warn.

    `docs/INSTALL.md` shipped a `margins` example that omitted --variable and
    --adspend, so the documented command reported +228,000 for the business in
    06-worked-examples.md that loses 160,750. The reference guard missed it
    because it only inspected references/ and platforms/. Documentation that
    tells a user to run a command is executable documentation, so it is run.
    """

    DOCS = ("docs/INSTALL.md", "README.md", "SKILL.md")

    def _examples(self, rel):
        path = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(path):
            return []
        out, buf = [], None
        for raw in read(path).split("\n"):
            line = raw.strip()
            if buf is not None:
                buf += " " + line.rstrip("\\").strip()
                if not line.endswith("\\"):
                    out.append(buf)
                    buf = None
                continue
            if not line.startswith("python3 scripts/cfo_calc.py"):
                continue
            if line.endswith("\\"):
                buf = line.rstrip("\\").strip()
            else:
                out.append(line)
        return out

    def test_every_documented_example_executes_without_warning(self):
        import subprocess
        checked = 0
        for rel in self.DOCS:
            for example in self._examples(rel):
                # shlex, not split(): a documented command may contain
                # quoted values or a path with spaces, and naive
                # splitting would test something the user never runs.
                argv = shlex.split(example)
                argv[0] = sys.executable
                argv[1] = os.path.join(ROOT, "scripts", "cfo_calc.py")
                r = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(
                    r.returncode, 0,
                    "%s documents a command that fails:\n  %s\n  %s"
                    % (rel, example, r.stderr.strip()[-300:]))
                self.assertNotIn(
                    '"WARNING"', r.stdout,
                    "%s documents an incomplete cost stack, so the number it "
                    "prints is not a profit:\n  %s" % (rel, example))
                checked += 1
        self.assertGreater(checked, 3,
                           "expected several documented examples, found %d" % checked)

    def test_install_guide_lists_every_command(self):
        import cfo_calc
        text = read(os.path.join(ROOT, "docs", "INSTALL.md"))
        missing = [c for c in cfo_calc.COMMANDS if c not in text]
        self.assertEqual(missing, [],
                         "docs/INSTALL.md does not mention command(s): %r" % missing)


class PublishedClaims(unittest.TestCase):
    """Numbers the documentation states about itself must be true.

    These drifted repeatedly: README said the compact core was 7,867
    characters while INSTALL.md said 7,873 and the file was 7,873; README
    claimed 10 reference tests when there were 12. Every published count is
    now derived and compared rather than trusted.
    """

    DOCS = ("README.md", "docs/INSTALL.md")

    def test_compact_core_size_claims_are_accurate(self):
        actual = len(read(os.path.join(ROOT, "platforms",
                                       "universal-compact-core.md")))
        checked = 0
        for rel in self.DOCS:
            path = os.path.join(ROOT, *rel.split("/"))
            if not os.path.exists(path):
                continue
            for line in read(path).split("\n"):
                if "8,000" not in line:
                    continue
                m = re.search(r"([\d,]+)\s*(?:chars|characters)", line)
                if not m:
                    continue
                claimed = int(m.group(1).replace(",", ""))
                self.assertEqual(
                    claimed, actual,
                    "%s claims universal-compact-core.md is %d characters; "
                    "it is %d" % (rel, claimed, actual))
                checked += 1
        self.assertGreater(checked, 0, "no size claim found to verify")

    def test_repository_tree_test_counts_are_accurate(self):
        checked = 0
        for line in read(os.path.join(ROOT, "README.md")).split("\n"):
            m = re.search(r"(test_[a-z_]+\.py)\s+(\d+)\s+(?:\S+\s+)?tests", line)
            if not m:
                continue
            fname, claimed = m.group(1), int(m.group(2))
            path = os.path.join(ROOT, "scripts", fname)
            self.assertTrue(os.path.exists(path),
                            "README references a missing test file: %s" % fname)
            actual = len(re.findall(r"\n    def test_", read(path)))
            self.assertEqual(claimed, actual,
                             "README claims %s has %d tests; it has %d"
                             % (fname, claimed, actual))
            checked += 1
        self.assertGreaterEqual(
            checked, 3, "expected three test files in the README tree, found %d"
            % checked)

    def test_version_is_declared_identically_everywhere(self):
        """A partial sweep leaves the repository claiming two versions."""
        import json
        found = {}
        skill = read(os.path.join(ROOT, "SKILL.md"))
        found["SKILL.md"] = re.search(r"^\s*version:\s*(\S+)", skill, re.M).group(1)
        found["SKILL.md signature"] = re.search(
            r"^\s*signature:\s*MKH-EBIC-(\S+)", skill, re.M).group(1)
        found["README badge"] = re.search(
            r"badge/version-([0-9.]+)-",
            read(os.path.join(ROOT, "README.md"))).group(1)
        man = json.loads(read(os.path.join(ROOT, "SIGNATURE.json")))
        found["SIGNATURE.json"] = man["version"]
        found["SIGNATURE.json signature"] = man["signature"].replace("MKH-EBIC-", "")
        found["verify_signature.py"] = re.search(
            r'VERSION = "([^"]+)"',
            read(os.path.join(ROOT, "scripts", "verify_signature.py"))).group(1)
        found["CITATION.cff"] = re.search(
            r"^version:\s*[\"']?([0-9.]+)",
            read(os.path.join(ROOT, "CITATION.cff")), re.M).group(1)
        found["llms.txt"] = re.search(
            r"Current version:\s*([0-9]+\.[0-9]+\.[0-9]+)",
            read(os.path.join(ROOT, "llms.txt"))).group(1)
        self.assertEqual(len(set(found.values())), 1,
                         "version declared inconsistently: %r" % (found,))

    def test_changelog_documents_the_current_version(self):
        current = re.search(r"^\s*version:\s*(\S+)",
                            read(os.path.join(ROOT, "SKILL.md")), re.M).group(1)
        self.assertRegex(
            read(os.path.join(ROOT, "CHANGELOG.md")),
            r"##\s*%s\b" % re.escape(current),
            "CHANGELOG has no entry for the current version %s" % current)

    def test_prose_only_cites_versions_that_exist(self):
        """A blanket sweep has three times rewritten historical prose such as
        "before v2.2.1" into a version that never carried that meaning. Every
        version named anywhere must at least appear in the CHANGELOG."""
        known = set(re.findall(r"^##\s*([0-9]+\.[0-9]+\.[0-9]+)",
                               read(os.path.join(ROOT, "CHANGELOG.md")), re.M))
        self.assertTrue(known, "no versions parsed from CHANGELOG")
        offenders = []
        for rel in ("README.md", "docs/INSTALL.md", "SKILL.md",
                    "scripts/pl_model.py", "scripts/cfo_calc.py",
                    "scripts/test_cfo_calc.py",
                    "scripts/test_reference_consistency.py"):
            path = os.path.join(ROOT, *rel.split("/"))
            if not os.path.exists(path):
                continue
            for cited in set(re.findall(r"v([0-9]+\.[0-9]+\.[0-9]+)", read(path))):
                if cited not in known:
                    offenders.append("%s cites v%s" % (rel, cited))
        self.assertEqual(
            offenders, [],
            "version(s) cited that the CHANGELOG never records: %r" % offenders)


class ReleaseProcess(unittest.TestCase):
    """The release mechanism itself, and the CI that runs untrusted code."""

    CI = os.path.join(ROOT, ".github", "workflows", "ci.yml")

    def test_declarations_agree_and_history_is_intact(self):
        import release_version
        problems = release_version.check(verbose=False)
        self.assertEqual(problems, [], "release_version --check reported: %r"
                         % problems)

    def _ci(self):
        if not os.path.exists(self.CI):
            self.skipTest("no CI workflow present")
        return read(self.CI)

    def test_ci_declares_least_privilege(self):
        """A fork pull request runs untrusted code with this token."""
        ci = self._ci()
        self.assertRegex(
            ci, r"(?m)^permissions:\s*$",
            "ci.yml declares no permissions block, so the workflow inherits "
            "the repository default, which may include write access")
        self.assertRegex(ci, r"(?m)^\s+contents:\s*read\s*$",
                         "ci.yml does not restrict contents to read")
        for forbidden in ("contents: write", "packages: write",
                          "pull-requests: write", "issues: write",
                          "id-token: write"):
            self.assertNotIn(forbidden, ci,
                             "ci.yml grants %r to untrusted PR code" % forbidden)

    def test_ci_does_not_use_pull_request_target(self):
        self.assertNotIn(
            "pull_request_target", self._ci(),
            "pull_request_target runs trusted-context code against an "
            "attacker-controlled branch")

    def test_ci_pins_actions_to_immutable_shas(self):
        floating = re.findall(r"uses:\s*([\w./-]+)@(v?\d+(?:\.\d+)*)\s*$",
                              self._ci(), re.M)
        self.assertEqual(floating, [],
                         "action(s) pinned to a movable tag: %r" % floating)
        self.assertTrue(re.search(r"uses:\s*[\w./-]+@[0-9a-f]{40}", self._ci()),
                        "expected at least one SHA-pinned action")

    def test_ci_does_not_pipe_downloads_into_a_shell(self):
        ci = self._ci()
        for pattern in ("curl", "wget", "| bash", "| sh"):
            self.assertNotIn(pattern, ci,
                             "ci.yml fetches or pipes external code: %r" % pattern)

    def test_ci_defines_no_secrets(self):
        self.assertNotIn("secrets.", self._ci(),
                         "ci.yml exposes a secret to pull-request code")


if __name__ == "__main__":
    unittest.main(verbosity=2)
