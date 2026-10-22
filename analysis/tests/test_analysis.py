"""The fake-data tests of DESIGN.md section 9.2, numbered as there.

    cd analysis && python3 -m unittest -v tests.test_analysis

Each fake grid is written to a temporary folder and removed afterwards. Test 6 reads the
certifying smoke set (default: the smoke-runs folder beside the plan, or MRV_SMOKE_RUNS) and is
skipped if it is not there. MRV_QUICK=1 runs the simulation tests with fewer grids.
"""
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import numpy as np  # noqa: E402

from mrv import analyse, config, describe, fakedata, load, power, stats  # noqa: E402

QUICK = os.environ.get("MRV_QUICK") == "1"
SMOKE = Path(os.environ.get("MRV_SMOKE_RUNS", HERE.parents[2] / "smoke-runs"))
MODELS = {"gemma-q4", "gptoss-20b"}          # one model with an OFF arm, one without
FAST = analyse.Settings(n_perm=2000, n_boot=2000)


def make(sc, seed="test", models=MODELS, **kw):
    """Write a fake grid into a fresh temporary folder: (plan, paths, table)."""
    root = Path(tempfile.mkdtemp(prefix="mrv-"))
    plan = fakedata.make_plan(sc, seed, models=models)
    paths = fakedata.write_grid(plan, root, **kw)
    table = load.build_table(paths["key"], paths["runs"], paths["results"], paths["state"],
                             fakedata.RUBRICS, paths["probe"], paths["power"])
    return root, plan, paths, table


def same(x, y):
    if isinstance(x, float) and isinstance(y, float):
        if math.isnan(x) or math.isnan(y):
            return math.isnan(x) and math.isnan(y)
        return abs(x - y) <= 1e-6 * max(1.0, abs(y))
    return x == y


class T1NullCalibration(unittest.TestCase):
    """1. A null grid rejects each test about 5% of the time, and Holm keeps each family's rate
    at or below 5%."""

    def test_null_rates(self):
        n = 200 if QUICK else 1000
        st = analyse.Settings(n_perm=1000, n_boot=200)
        for name, a, b, kind in power.scenarios():
            if "null" not in name:
                continue
            rows = power.run_scenario(name, a, b, kind, n, st, seed_label="t1")
            for r in rows:
                if r["verdict"] in ("different", "supported"):
                    # A single test after Holm rejects at most at alpha. Allow three Monte Carlo SEs.
                    self.assertLessEqual(r["share"], 0.05 + 3 * math.sqrt(0.05 * 0.95 / n), (name, r))
                if r["verdict"] == "any rejection":
                    self.assertLessEqual(r["share"], 0.05 + 3 * math.sqrt(0.05 * 0.95 / n), (name, r))

    def test_unadjusted_rate_near_alpha(self):
        """Before Holm, a single stratified permutation test rejects at about alpha."""
        import numpy as np
        n = 300 if QUICK else 1500
        rng = np.random.default_rng(1)
        rej = 0
        for i in range(n):
            rows = power.simulate(power.arm_params(p_fail=0.2), power.arm_params(p_fail=0.2), rng)
            v, b, s = analyse._pick(rows, "sim", "unseen", "seen", "log_steps")
            _, p, _, _ = stats.perm_test(v, b, s, 1000, rng)
            rej += p < 0.05
        rate = rej / n
        self.assertLess(abs(rate - 0.05), 3 * math.sqrt(0.05 * 0.95 / n) + 0.005, rate)

    def test_interval_formulas(self):
        """Wilson and Newcombe against the worked examples of Newcombe (1998), Statistics in
        Medicine 17, 873-890 and 857-872."""
        lo, hi = stats.newcombe(48, 80, 56, 70)
        self.assertAlmostEqual(lo, 0.0524, places=4)
        self.assertAlmostEqual(hi, 0.3339, places=4)
        lo, hi = stats.wilson(81, 263)
        self.assertAlmostEqual(lo, 0.2553, places=4)
        self.assertAlmostEqual(hi, 0.3662, places=4)

    def test_rescaled_bootstrap_variance(self):
        """The rescaled stratified bootstrap gives the unbiased variance of a stratified mean."""
        import numpy as np
        rng = np.random.default_rng(3)
        v = rng.normal(size=60)
        s = np.repeat(np.arange(6), 10)
        m = stats._boot_means(v, s, 200000, rng)
        want = sum(v[s == h].var(ddof=1) * 10 for h in range(6)) / 60 ** 2
        self.assertAlmostEqual(m.var() / want, 1.0, delta=0.02)

    def test_holm(self):
        self.assertEqual([round(x, 6) for x in stats.holm([0.01, 0.03, 0.02])], [0.03, 0.04, 0.04])
        out = stats.holm([0.5, float("nan"), 0.01])
        self.assertTrue(math.isnan(out[1]))
        self.assertAlmostEqual(out[2], 0.02)


class T2Recovery(unittest.TestCase):
    """2. Planted effects are found, and intervals cover the planted value at about the nominal rate."""

    @classmethod
    def setUpClass(cls):
        sc = fakedata.scenario()
        sc["cells"].append(({"arm": "seen"}, {"p_fail": 0.02, "steps_mu": math.log(40), "q_works": 0.9,
                                              "rate": 0.99, "med_chars": 120.0, "p_silent": 0.0}))
        sc["cells"].append(({"arm": "unseen"}, {"p_fail": 0.35, "q_works": 0.3, "rate": 0.6,
                                                "med_chars": 400.0, "p_silent": 0.4}))
        cls.root, cls.plan, cls.paths, cls.table = make(sc, "t2")
        cls.res = analyse.confirmatory(cls.table["rows"], FAST)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_found(self):
        got = {(r["model"], r["family"], r["measure"]): r for r in self.res}
        for m in MODELS:
            for meas in ("failure", "steps", "quality"):
                self.assertEqual(got[(m, "H1", meas)]["verdict"], "different", (m, meas))
            for h in ("H3", "H4", "H5"):
                self.assertEqual(got[(m, "H3-H5", h)]["verdict"], "supported", (m, h))
        self.assertIn(("gemma-q4", "H2", "failure"), got)
        self.assertNotIn(("gptoss-20b", "H2", "failure"), got)

    def test_estimates_near_planted(self):
        got = {(r["model"], r["family"], r["measure"]): r for r in self.res}
        for m in MODELS:
            f = got[(m, "H1", "failure")]
            self.assertLess(f["ci95_lo"], 0.02 - 0.35 + 0.1)
            self.assertLess(f["ci95_lo"], f["estimate"])
            self.assertGreater(f["ci95_hi"], f["estimate"])
            s = got[(m, "H1", "steps")]
            self.assertTrue(s["ci95_lo"] < 40 / 60 < s["ci95_hi"], s)

    def test_coverage(self):
        n = 100 if QUICK else 400
        for r in power.coverage(n_grids=n, n_boot=1000):
            tol = 3 * math.sqrt(0.05 * 0.95 / n) + 0.02
            self.assertGreater(r["coverage95"], 0.95 - tol, r)
            self.assertGreater(r["coverage90"], 0.90 - tol, r)


class T3Determinism(unittest.TestCase):
    """3. Two runs with the same seeds give byte-identical output."""

    def test_identical(self):
        root, plan, paths, _ = make(fakedata.scenario(p_void=0.05), "t3", models={"gemma-q4"})
        try:
            outs = []
            for k in range(2):
                out = root / f"out{k}"
                import run_analysis
                rc = run_analysis.main(["--key", str(paths["key"]), "--runs", str(paths["runs"]),
                                        "--state", str(paths["state"]), "--results", str(paths["results"]),
                                        "--power", str(paths["power"]), "--out", str(out),
                                        "--n-perm", "500", "--n-boot", "500"])
                self.assertEqual(rc, 0)
                outs.append(out)
            files = sorted(str(p.relative_to(outs[0])) for p in outs[0].rglob("*") if p.is_file())
            self.assertIn("intermediate/bootstrap-replicates.csv.gz", files)
            for f in files:
                self.assertEqual((outs[0] / f).read_bytes(), (outs[1] / f).read_bytes(), f)
            # And the plan itself is reproducible from its seed.
            again = fakedata.make_plan(fakedata.scenario(p_void=0.05), "t3", models={"gemma-q4"})
            self.assertEqual([a["blind_id"] for a in again["attempts"]], [a["blind_id"] for a in plan["attempts"]])
        finally:
            shutil.rmtree(root, ignore_errors=True)


class T4EdgeCases(unittest.TestCase):
    """4. Edge cases, and the round trip from planted values through the files to the run table."""

    def test_round_trip(self):
        root, plan, paths, table = make(fakedata.scenario(p_void=0.05), "t4a", regrade_per_cell=1)
        try:
            truth = fakedata.truth_rows(plan, paths["sample"])
            rows = {r["blind_id"]: r for r in table["rows"]}
            self.assertEqual(set(rows), set(truth))
            for bid, t in truth.items():
                for k, v in t.items():
                    self.assertTrue(same(rows[bid][k], v), (bid, k, v, rows[bid][k]))
            self.assertEqual(len(table["ungraded"]), 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_edges(self):
        sc = fakedata.scenario(p_nudge=1.0, p_sub=1.0)
        sc["cells"].append(({"arm": "seen"}, {"p_fail": 0.0}))                       # an arm with no failures
        sc["cells"].append(({"task": "kanban-board", "condition": "interactive", "arm": "unseen"},
                            {"p_void": 1.0}))                                         # a stratum of voids
        sc["cells"].append(({"model": "gptoss-20b", "arm": "unseen"}, {"rate": 0.0}))  # no reasoning step
        root, plan, paths, table = make(sc, "t4b", extend_to=12)
        try:
            rows = table["rows"]
            # Every slot of the void stratum is empty, and counted.
            self.assertEqual(len(table["voids"]["slots"]), 2 * 20)
            v = describe.voids(table["voids"], rows)
            self.assertTrue(all(r["empty_slots"] in (0, 20) for r in v))
            res = analyse.run_all(rows, FAST)
            got = {(r["analysis"], r["model"], r["family"], r["measure"]): r for r in
                   res["confirmatory"] + res["sensitivity"]}
            # No failures in SEEN: the failure contrast still has an interval.
            f = got[("confirmatory", "gemma-q4", "H1", "failure")]
            self.assertTrue(f["ci95_lo"] == f["ci95_lo"])
            # No reasoning step in gpt-oss UNSEEN: H4 has no data there, and says so.
            self.assertEqual(got[("confirmatory", "gptoss-20b", "H3-H5", "H4")]["verdict"], "no data")
            # Every run nudged: the no-nudge sensitivity has no data.
            self.assertEqual(got[("no-nudge", "gemma-q4", "H1", "failure")]["verdict"], "no data")
            # Every app substituted: scored 0, the substituted-0 quality means are 0.
            s = got[("substituted-0", "gemma-q4", "H1", "quality")]
            self.assertEqual((s["mean_a"], s["mean_b"]), (0.0, 0.0))
            # The extended sample grades 12 of every cell (fewer where voids took places).
            per_cell = Counter((r["model"], r["task"], r["condition"], r["arm"]) for r in rows if r["sampled"] == 1.0)
            self.assertLessEqual(max(per_cell.values()), 12)
            self.assertGreaterEqual(statistics.median(per_cell.values()), 11)
            # The descriptives and the compute table are made without error.
            describe.per_cell(rows, analyse.Settings(0, 200))
            describe.compute(rows, table["spans"])
        finally:
            shutil.rmtree(root, ignore_errors=True)


class T4bVoidsAndOutcomes(unittest.TestCase):
    """4, continued. The void rule of protocol section 9: an overflow filed as an API error is an
    outcome, and a void the runner could not see (a configuration that differs, the npm
    registry unreachable) stops the analysis until its slot is re-run. Also the statuses list,
    the energy integral, and the registered exploratory rows."""

    @classmethod
    def setUpClass(cls):
        cls.root, cls.plan, cls.paths, _ = make(fakedata.scenario(), "t4b2", models={"gptoss-20b"})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def fresh(self):
        d = Path(tempfile.mkdtemp(prefix="mrv-t4b-"))
        shutil.copytree(self.root / "runs", d / "runs")
        shutil.copy(self.paths["key"], d / "key.jsonl")
        return d

    def key(self, d):
        return [json.loads(x) for x in (d / "key.jsonl").read_text().splitlines() if x.strip()]

    def logs(self, d, rec):
        return d / "runs" / rec["model_key"] / rec["task"] / "runs" / rec["blind_id"] / "smoke" / "logs"

    def rerun(self, d, rec, source):
        """A later attempt of rec's slot: a copy of another run's folder under a new id."""
        new = dict(rec, blind_id="9" + rec["blind_id"][1:], started_at="2099-01-01T00:00:00+00:00", agent_rc=0)
        dest = d / "runs" / rec["model_key"] / rec["task"] / "runs" / new["blind_id"]
        shutil.copytree(self.logs(d, source).parent.parent, dest)
        with open(d / "key.jsonl", "a") as f:
            f.write(json.dumps(new) + "\n")
        return new

    def test_overflow_filed_as_error_is_an_outcome(self):
        d = self.fresh()
        try:
            recs = self.key(d)
            rec = next(r for r in recs if r["status"] == "finished")
            m = self.logs(d, rec) / "manifest.json"
            man = json.loads(m.read_text())
            man["status"] = "api_error"
            man["api_error"] = {"code": 400, "body": '{"error":{"code":400,"message":"request (70000 tokens) exceeds '
                                'the available context size (65536 tokens)","type":"exceed_context_size_error"}}'}
            m.write_text(json.dumps(man))
            # An older harness exits 1 here, so the batch driver re-runs the slot.
            lines = [dict(r, agent_rc=1) if r["blind_id"] == rec["blind_id"] else r for r in recs]
            (d / "key.jsonl").write_text("".join(json.dumps(r) + "\n" for r in lines))
            other = next(r for r in recs if r["blind_id"] != rec["blind_id"] and r["task"] == rec["task"])
            new = self.rerun(d, rec, other)
            t = load.build_table(d / "key.jsonl", d / "runs")
            row = {r["blind_id"]: r for r in t["rows"]}
            self.assertIn(rec["blind_id"], row)
            self.assertEqual(row[rec["blind_id"]]["status"], "context_overflow")
            self.assertEqual(row[rec["blind_id"]]["failed"], 1.0)
            self.assertNotIn(new["blind_id"], row)
            self.assertEqual([a["blind_id"] for a in t["voids"]["after_outcome"]], [new["blind_id"]])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_npm_unreachable_stops_until_rerun(self):
        d = self.fresh()
        try:
            recs = self.key(d)
            rec = next(r for r in recs if r["agent_rc"] == 0)
            with open(self.logs(d, rec) / "trace.jsonl", "a") as f:
                f.write(json.dumps({"kind": "tool_result", "step": 2, "tool": "run_command",
                                    "result": "$ cd backend && npm install\n[exit 1]\nnpm error code ENOTFOUND\n"
                                              "npm error network request to https://registry.npmjs.org/express failed"}) + "\n")
            with self.assertRaises(load.InputError) as cm:
                load.build_table(d / "key.jsonl", d / "runs")
            self.assertIn(rec["label"], str(cm.exception))
            self.assertIn("npm registry unreachable", str(cm.exception))
            self.assertNotIn(rec["blind_id"], str(cm.exception))
            import run_analysis
            self.assertEqual(run_analysis.main(["check", "--key", str(d / "key.jsonl"), "--runs", str(d / "runs")]), 2)
            other = next(r for r in recs if r["blind_id"] != rec["blind_id"] and r["task"] == rec["task"] and r["agent_rc"] == 0)
            new = self.rerun(d, rec, other)
            self.assertEqual(run_analysis.main(["check", "--key", str(d / "key.jsonl"), "--runs", str(d / "runs")]), 0)
            t = load.build_table(d / "key.jsonl", d / "runs")
            ids = {r["blind_id"] for r in t["rows"]}
            self.assertIn(new["blind_id"], ids)
            self.assertNotIn(rec["blind_id"], ids)
            cause = {a["blind_id"]: a["cause"] for a in t["voids"]["attempts"]}
            self.assertTrue(cause[rec["blind_id"]].startswith("re-run by hand: npm registry unreachable"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_wrong_model_file_stops(self):
        d = self.fresh()
        try:
            rec = next(r for r in self.key(d) if r["agent_rc"] == 0)
            m = self.logs(d, rec) / "manifest.json"
            man = json.loads(m.read_text())
            man["quantization_detail"] = {"status": "rung_missing"}
            m.write_text(json.dumps(man))
            with self.assertRaises(load.InputError) as cm:
                load.build_table(d / "key.jsonl", d / "runs")
            self.assertIn("quantization_detail", str(cm.exception))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_statuses_energy_and_rows(self):
        t = load.build_table(self.paths["key"], self.paths["runs"], self.paths["results"], self.paths["state"],
                             fakedata.RUBRICS, self.paths["probe"], self.paths["power"])
        rows = t["rows"]
        self.assertTrue({r["status"] for r in rows} <= set(config.STATUSES))
        self.assertNotIn("api_error", config.STATUSES)
        for r in rows:
            # The fake power log holds a constant 250 W over every run's span.
            self.assertAlmostEqual(r["energy_wh"], r["machine_s"] * 250.0 / 3600.0, places=6)
            self.assertIsInstance(r["finish_nudge_steps"], list)
        res = analyse.exploratory(rows, FAST)
        kinds = Counter(r["analysis"] for r in res)
        self.assertEqual(kinds["verification:difference"], 3)
        self.assertEqual(kinds["quality:finished"], 1)
        desc = describe.per_cell(rows, FAST)
        q = {(d["arm"], d["quantity"]) for d in desc}
        for s in config.STATUSES:
            self.assertIn(("seen", f"status:{s}"), q)
        self.assertIn(("seen", "canary:runs_over"), q)

    def test_pairs_reuse_confirmatory(self):
        root, plan, paths, table = make(fakedata.scenario(), "t4b3", models={"qwen-q4", "qwen-moe-q4"})
        try:
            conf = {(r["model"], r["family"], r["measure"]): r for r in analyse.confirmatory(table["rows"], FAST)}
            for r in analyse.exploratory(table["rows"], FAST):
                if r["analysis"] in ("pair:twin", "pair:sibling"):
                    c = conf[(r["model"], r["family"], r["measure"])]
                    self.assertEqual((r["estimate"], r["ci95_lo"], r["ci95_hi"]), (c["estimate"], c["ci95_lo"], c["ci95_hi"]))
        finally:
            shutil.rmtree(root, ignore_errors=True)


class T5InputChecks(unittest.TestCase):
    """5. The input checks refuse a mismatched harness_git, a missing manifest, an orphan key line
    and a run with no key line."""

    @classmethod
    def setUpClass(cls):
        cls.root, cls.plan, cls.paths, _ = make(fakedata.scenario(), "t5", models={"gptoss-20b"})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def fresh(self):
        d = Path(tempfile.mkdtemp(prefix="mrv-t5-"))
        shutil.copytree(self.root / "runs", d / "runs", symlinks=True)
        shutil.copy(self.paths["key"], d / "key.jsonl")
        return d

    def refuses(self, d, pattern):
        with self.assertRaises(load.InputError) as cm:
            load.build_table(d / "key.jsonl", d / "runs")
        self.assertRegex(str(cm.exception), pattern)
        shutil.rmtree(d, ignore_errors=True)

    def first_manifest(self, d):
        a = self.plan["attempts"][0]
        return d / "runs" / a["model"] / a["task"] / "runs" / a["blind_id"] / "smoke" / "logs" / "manifest.json"

    def test_harness_git(self):
        d = self.fresh()
        m = self.first_manifest(d)
        man = json.loads(m.read_text())
        man["harness_git"] = "5ac366f4175dc0929c28ad45e1560d26760f83fa"
        m.write_text(json.dumps(man))
        self.refuses(d, "harness_git")

    def test_missing_manifest(self):
        d = self.fresh()
        m = self.first_manifest(d)
        m.rename(m.with_name("manifest.moved"))
        self.refuses(d, "key line without a run")

    def test_orphan_key_line(self):
        d = self.fresh()
        rec = json.loads((d / "key.jsonl").read_text().splitlines()[0])
        rec["blind_id"] = "999999"
        with open(d / "key.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        self.refuses(d, "999999: key line without a run")

    def test_run_without_key_line(self):
        d = self.fresh()
        lines = (d / "key.jsonl").read_text().splitlines()
        (d / "key.jsonl").write_text("\n".join(lines[1:]) + "\n")
        self.refuses(d, "a run with no key line")

    def test_clean_grid_loads(self):
        d = self.fresh()
        load.build_table(d / "key.jsonl", d / "runs")
        shutil.rmtree(d, ignore_errors=True)


class T7IntermediateRecord(unittest.TestCase):
    """7. Every final number can be rebuilt from the intermediate record alone (DESIGN.md
    section 12): the run table from the steps and the scores, each estimate from its units,
    each interval from its replicates or its Newcombe pieces, each p from its permuted
    statistics, Holm from its steps, and the verdicts."""

    @classmethod
    def setUpClass(cls):
        import run_analysis
        cls.root = Path(tempfile.mkdtemp(prefix="mrv-t7-"))
        sc = fakedata.scenario(p_void=0.05, p_nudge=0.2, p_sub=0.1)
        sc["cells"].append(({"arm": "seen"}, {"p_fail": 0.05, "q_works": 0.85, "rate": 0.98, "p_silent": 0.0}))
        plan = fakedata.make_plan(sc, "t7", models={"gemma-q4", "gptoss-20b"}, max_replicate=6)
        paths = fakedata.write_grid(plan, cls.root / "grid")
        cls.out = cls.root / "out"
        rc = run_analysis.main(["--key", str(paths["key"]), "--runs", str(paths["runs"]), "--state", str(paths["state"]),
                                "--results", str(paths["results"]), "--power", str(paths["power"]),
                                "--out", str(cls.out), "--n-perm", "1000", "--n-boot", "1000"])
        assert rc == 0
        cls.im = cls.out / "intermediate"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def csv(self, path):
        import csv as _csv
        with open(path, encoding="utf-8") as f:
            return list(_csv.DictReader(f))

    def series(self, name):
        import gzip
        out = {}
        with gzip.open(self.im / name, "rt", encoding="utf-8") as f:
            next(f)
            for line in f:
                parts = line.rstrip("\n").split(",")
                out[parts[0]] = np.array([float(x) for x in parts[2:]]) if int(parts[1]) else np.array([])
                self.assertEqual(int(parts[1]), out[parts[0]].size)
        return out

    @staticmethod
    def f(x):
        return float(x) if x not in ("", None) else float("nan")

    @staticmethod
    def probs(level):
        """The quantile probabilities, as the intermediate README states them."""
        lo = (1.0 - level) / 2.0
        return [lo, 1.0 - lo]

    def close6(self, a, b, what):
        """A full-precision value against a final table's 6-significant-digit one."""
        a, b = self.f(a), self.f(b)
        if math.isnan(a) or math.isnan(b):
            self.assertTrue(math.isnan(a) and math.isnan(b), what)
        else:
            self.assertEqual(float(f"{a:.6g}"), b, what)

    def test_run_table_from_steps_scores_attempts(self):
        rt = {r["blind_id"]: r for r in self.csv(self.out / "run-table.csv")}
        analysed = {r["blind_id"] for r in self.csv(self.im / "attempts.csv") if r["role"] == "analysed run of its slot"}
        self.assertEqual(analysed, set(rt))
        steps = defaultdict(list)
        for r in self.csv(self.im / "steps.csv"):
            steps[r["blind_id"]].append(r)
        for bid, row in rt.items():
            xs = steps[bid]
            n = len(xs)
            lens = [int(x["reasoning_chars"]) for x in xs]
            thinking = [x for x in lens if x]
            self.assertEqual(n, int(row["trace_steps"]))
            self.close6(len(thinking) / n, row["reasoning_rate"], (bid, "rate"))
            self.close6(statistics.median(thinking) if thinking else float("nan"), row["reasoning_median_chars"], (bid, "median"))
            self.close6(1.0 if any(int(x["silent"]) for x in xs) else 0.0, row["silent_turn"], (bid, "silent"))
            self.close6(sum(int(x["call_as_text"]) for x in xs), row["call_as_text_steps"], (bid, "callTxt"))
            self.close6(max(int(x["canary_chars"]) for x in xs), row["canary_longest_chars"], (bid, "canary"))
        scores = {r["blind_id"]: r for r in self.csv(self.im / "scores.csv") if r["role"] == "first grading"}
        for bid, row in rt.items():
            if row["sampled"] == "1":
                s = scores[bid]
                q = round(100.0 * float(s["weight_passed"]) / float(s["weight_scored"]), 2)
                self.assertEqual(q, float(s["score"]))
                self.close6(q, row["quality"], (bid, "quality"))
                self.assertEqual(s["substituted"], row["substituted"])

    def test_estimates_intervals_p(self):
        final = {r["test_id"]: r for name in ("confirmatory", "sensitivity", "exploratory")
                 for r in self.csv(self.out / f"{name}.csv")}
        detail = {r["test_id"]: r for r in self.csv(self.im / "test-detail.csv")}
        units = defaultdict(list)
        for r in self.csv(self.im / "test-units.csv"):
            if r["used"] == "1":
                units[r["test_id"]].append(r)
        boot = self.series("bootstrap-replicates.csv.gz")
        perm = self.series("permutation-statistics.csv.gz")
        self.assertTrue(set(final) <= set(detail))
        checked = Counter()
        for tid, d in detail.items():
            if "of_first" in d and d["of_first"]:
                e = self.f(detail[d["of_first"]]["estimate"])
                e2 = self.f(detail[d["of_second"]]["estimate"])
                want = e / e2 if d["combined"] == "ratio of the two" else e - e2
                self.assertAlmostEqual(self.f(d["estimate"]), want, places=12)
                if d["interval"] == "bootstrap":
                    q = np.quantile(boot[tid][np.isfinite(boot[tid])], self.probs(0.95))
                    self.assertEqual((float(q[0]), float(q[1])), (self.f(d["ci95_lo"]), self.f(d["ci95_hi"])))
                checked["difference"] += 1
                continue
            us = units[tid]
            va = [float(u["value"]) for u in us if u["arm_b"] == "0"]
            vb = [float(u["value"]) for u in us if u["arm_b"] == "1"]
            self.assertEqual((len(va), len(vb)), (int(d["n_a"]), int(d["n_b"])), tid)
            if va and vb:
                ma, mb = float(np.mean(va)), float(np.mean(vb))
                k = d["kind"]
                want = mb - ma if k == "diff" else math.exp(mb - ma) if k == "ratio_geo" else mb / ma
                self.assertAlmostEqual(self.f(d["estimate"]), want, delta=1e-12 * max(1.0, abs(want)))
            if d["interval"] == "bootstrap" and tid in boot and boot[tid].size:
                r = boot[tid][np.isfinite(boot[tid])]
                q95 = np.quantile(r, self.probs(0.95))
                q90 = np.quantile(r, self.probs(0.90))
                self.assertEqual((float(q95[0]), float(q95[1]), float(q90[0]), float(q90[1])),
                                 tuple(self.f(d[k]) for k in ("ci95_lo", "ci95_hi", "ci90_lo", "ci90_hi")), tid)
                self.assertEqual(r.size, int(d["n_boot"]))
                checked["bootstrap"] += 1
            if d["interval"] == "newcombe" and va and vb:
                pa, pb = float(np.mean(va)), float(np.mean(vb))
                for lev in ("95", "90"):
                    la, ua, lb, ub = (self.f(d[f"newcombe{lev}_wilson_{x}"]) for x in ("a_lo", "a_hi", "b_lo", "b_hi"))
                    # Wilson's interval, written out here apart from the code.
                    z = self.f(d[f"newcombe{lev}_z"])
                    for x, n, lo_, hi_ in ((sum(va), len(va), la, ua), (sum(vb), len(vb), lb, ub)):
                        ph = x / n
                        c = (ph + z * z / (2 * n)) / (1 + z * z / n)
                        h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
                        self.assertAlmostEqual(lo_, max(0.0, c - h), places=12)
                        self.assertAlmostEqual(hi_, min(1.0, c + h), places=12)
                    lo = (pb - pa) - math.sqrt((pb - lb) ** 2 + (ua - pa) ** 2)
                    hi = (pb - pa) + math.sqrt((ub - pb) ** 2 + (pa - la) ** 2)
                    self.assertAlmostEqual(lo, self.f(d[f"ci{lev}_lo"]), places=12)
                    self.assertAlmostEqual(hi, self.f(d[f"ci{lev}_hi"]), places=12)
                checked["newcombe"] += 1
            if d.get("alternative") and tid in perm:
                t = perm[tid]
                t_obs, eps = self.f(d["t_obs"]), self.f(d["tolerance"])
                alt = d["alternative"]
                ext = (np.abs(t) >= abs(t_obs) - eps) if alt == "two-sided" else (t >= t_obs - eps) if alt == "greater" else (t <= t_obs + eps)
                self.assertEqual(int(ext.sum()), int(d["extreme"]), tid)
                self.assertEqual((1 + int(ext.sum())) / (t.size + 1), self.f(d["p"]), tid)
                checked["p"] += 1
            if tid in final:
                for k in ("estimate", "ci95_lo", "ci95_hi", "ci90_lo", "ci90_hi", "p"):
                    if k in d and d[k] != "" and final[tid].get(k, "") != "":
                        self.close6(d[k], final[tid][k], (tid, k))
        self.assertGreater(checked["bootstrap"], 20)
        self.assertGreater(checked["newcombe"], 5)
        self.assertGreater(checked["p"], 20)
        self.assertGreater(checked["difference"], 3)

    def test_holm_and_verdicts(self):
        final = {r["test_id"]: r for name in ("confirmatory", "sensitivity")
                 for r in self.csv(self.out / f"{name}.csv")}
        fams = defaultdict(list)
        for r in self.csv(self.im / "holm.csv"):
            fams[r["family_id"]].append(r)
        for fid, rows in fams.items():
            rows.sort(key=lambda r: int(r["rank"]))
            m, running = len(rows), 0.0
            for r in rows:
                prod = min(1.0, (m - int(r["rank"]) + 1) * float(r["p"]))
                running = max(running, prod)
                self.assertEqual(running, float(r["adjusted_running_max"]), fid)
                self.assertEqual(running, float(r["p_holm"]), fid)
                if r["test_id"] in final:
                    self.close6(running, final[r["test_id"]]["p_holm"], r["test_id"])
        for v in self.csv(self.im / "verdicts.csv"):
            if v["test_id"] in final:
                self.assertEqual(v["verdict"], final[v["test_id"]]["verdict"])
            ph = float(v["p_holm"])
            if v["verdict"] == "different":
                self.assertLess(ph, 0.05)
            if v["verdict"] == "equivalent":
                self.assertTrue(float(v["bound_lo"]) < float(v["ci90_lo"]) and float(v["ci90_hi"]) < float(v["bound_hi"]))

    def test_describe_replicates(self):
        desc = [r for r in self.csv(self.out / "descriptives.csv") if r.get("interval") == "bootstrap"]
        reps = self.series("describe-replicates.csv.gz")
        for r in desc:
            x = reps[r["id"]]
            x = x[np.isfinite(x)]
            if x.size:
                q = np.quantile(x, self.probs(0.95))
                self.close6(float(q[0]), r["ci95_lo"], r["id"])
                self.close6(float(q[1]), r["ci95_hi"], r["id"])


ROW_RE = re.compile(r"^(\S+)\s+(OFF|UNSEEN|SEEN)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%\s+(\d+)\s+(\d+)\s+(.*)$")
ARM_OF = {"1": "off", "2": "unseen", "3": "seen"}


@unittest.skipUnless((SMOKE / "verify_smokes_result.txt").exists(), f"smoke set not found at {SMOKE}")
class T6SmokeReproduction(unittest.TestCase):
    """6. On the 66 real smoke runs, the run table's per-model, per-arm numbers equal those the
    smoke gate script printed (verify_smokes_result.txt)."""

    def test_reproduces(self):
        expected = {}
        for line in (SMOKE / "verify_smokes_result.txt").read_text(encoding="utf-8").splitlines():
            m = ROW_RE.match(line)
            if m:
                g = m.groups()
                expected[(g[0], g[1].lower())] = {
                    "runs": int(g[2]), "steps": int(g[3]), "noTool": int(g[4]), "empty": int(g[5]),
                    "callTxt": int(g[6]), "rsn%": int(g[9]), "median": int(g[11]),
                    "status": dict((s.split("x ", 1)[1], int(s.split("x ", 1)[0])) for s in g[12].split(", "))}
        self.assertEqual(len(expected), 22)
        # The smoke runs, laid out as the grid lays out its runs, with a key line each.
        tmp = Path(tempfile.mkdtemp(prefix="mrv-t6-"))
        try:
            key = tmp / "key.jsonl"
            n = 0
            lengths = defaultdict(list)
            with open(key, "w") as f:
                for trace in sorted(SMOKE.glob("*/*/*/runs/*/smoke/logs/trace.jsonl")):
                    run = trace.parents[2]
                    model, task, cond, cid = run.parts[-5], run.parts[-4], run.parts[-3], run.name
                    arm = ARM_OF[cid[0]]
                    bid = f"{config.CONDITIONS.index(cond)}{cid}"
                    dest = tmp / "runs" / model / task / "runs" / bid
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.symlink_to(run)
                    f.write(json.dumps({"blind_id": bid, "task": task, "condition": cond, "arm": arm,
                                        "model_key": model, "label": f"{model}/{task}/{cond}/{arm}/r{int(cid[1:]):02d}",
                                        "agent_rc": 0}) + "\n")
                    lengths[(model, arm)] += [x for x in load.trace_measures(run / "smoke" / "logs")["reasoning_lengths"] if x]
                    n += 1
            self.assertEqual(n, 66)
            # The smoke set was made by the certifying harness commit, not the grid's.
            reg = dict(config.REGISTERED, harness_git="5ac366f4175dc0929c28ad45e1560d26760f83fa")
            rows = load.build_table(key, tmp / "runs", registered=reg)["rows"]
            got = defaultdict(lambda: Counter())
            status = defaultdict(Counter)
            for r in rows:
                c = got[(r["model"], r["arm"])]
                c["runs"] += 1
                c["steps"] += int(r["trace_steps"])
                c["noTool"] += int(r["no_tool_turns"])
                c["empty"] += int(r["silent_turns"])
                c["callTxt"] += int(r["call_as_text_steps"])
                c["thinking"] += int(r["thinking_steps"])
                status[(r["model"], r["arm"])][r["status"]] += 1
            self.assertEqual(set(got), set(expected))
            for k, e in expected.items():
                g = got[k]
                for col in ("runs", "steps", "noTool", "empty", "callTxt"):
                    self.assertEqual(g[col], e[col], (k, col))
                self.assertEqual(int(f"{100 * g['thinking'] / max(g['steps'], 1):.0f}"), e["rsn%"], k)
                med = int(statistics.median(lengths[k])) if lengths[k] else 0
                self.assertEqual(med, e["median"], k)
                self.assertEqual(dict(status[k]), e["status"], k)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
