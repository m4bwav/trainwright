FAKE_IP = ".".join(["192", "168", "1", "5"])  # built at runtime so the leak scan of this file stays clean
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TW = ROOT / "skills" / "trainwright" / "scripts" / "tw.py"


def run(*args, env=None):
    e = dict(os.environ, **(env or {}))
    p = subprocess.run([sys.executable, str(TW), *args], capture_output=True, text=True, env=e)
    try:
        return p.returncode, json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, {"raw": p.stdout + p.stderr}


class TwTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)
        self.home = self.d / "home"
        self.home.mkdir()
        (self.home / "hosts.json").write_text(json.dumps({"disk_floor_gb": 0}))
        self.env = {"TRAINWRIGHT_HOME": str(self.home)}
        ds = self.d / "ds"
        ds.mkdir()
        for i in range(3):
            (ds / f"{i}.png").write_bytes(b"img%d" % i)
            (ds / f"{i}.txt").write_text("a caption")
        self.ds = ds
        base = self.d / "base.safetensors"
        base.write_bytes(b"weights")
        self.base = base

    def tearDown(self):
        self.td.cleanup()

    def make(self, **over):
        rp = self.d / "r.recipe.json"
        code, o = run("new", "image-lora", "r", "--out", str(rp), "--force", env=self.env)
        self.assertEqual(code, 0, o)
        r = json.loads(rp.read_text())
        _, h = run("hash", str(self.base))
        _, m = run("hash", str(self.ds), "--manifest", "--source", "own photos")
        r["base"].update(name="z-image-base", path=str(self.base), sha256=h["sha256"], licence="apache-2.0")
        r["dataset"].update(root=str(self.ds), items=m["items"], licence="own")
        r["output"]["dir"] = str(self.d / "out" / "r")
        for k, v in over.items():
            sect, key = k.split("__")
            r[sect][key] = v
        rp.write_text(json.dumps(r))
        return rp

    def check(self, rp):
        return run("check", str(rp), env=self.env)

    def test_clean_recipe_passes(self):
        code, o = self.check(self.make())
        self.assertEqual(code, 0, o)

    def test_noncommercial_data_blocks_sellable(self):
        rp = self.make(dataset__licence="CC BY-NC 4.0")
        r = json.loads(rp.read_text()); r["use"] = "sellable"; rp.write_text(json.dumps(r))
        code, o = self.check(rp)
        self.assertEqual(code, 2)
        self.assertTrue(any("non-commercial" in f for f in o["fail"]))

    def test_krea2_banned_when_sellable(self):
        rp = self.make(base__name="krea-2-dev")
        r = json.loads(rp.read_text()); r["use"] = "sellable"; rp.write_text(json.dumps(r))
        code, o = self.check(rp)
        self.assertTrue(any("Krea" in f for f in o["fail"]))

    def test_subject_needs_consent(self):
        code, o = self.check(self.make(dataset__subject="a relative"))
        self.assertEqual(code, 2)
        self.assertTrue(any("consent" in f for f in o["fail"]))
        rp = self.make(dataset__subject="me", dataset__consent="self")
        self.assertEqual(self.check(rp)[0], 0)

    def test_strength_zero_control_required(self):
        code, o = self.check(self.make(eval__strengths=[0.8, 1.0]))
        self.assertTrue(any("strength-0" in f for f in o["fail"]))

    def test_changed_dataset_file_detected(self):
        rp = self.make()
        (self.ds / "0.png").write_bytes(b"changed")
        code, o = self.check(rp)
        self.assertTrue(any("changed" in f for f in o["fail"]))

    def test_nonempty_output_dir_blocks_same_name(self):
        rp = self.make()
        od = self.d / "out" / "r"; od.mkdir(parents=True); (od / "x").write_text("x")
        code, o = self.check(rp)
        self.assertTrue(any("resume" in f for f in o["fail"]))

    def test_config_aitoolkit_has_seed_and_save_every(self):
        rp = self.make()
        code, o = run("config", str(rp), "--trainer", "ai-toolkit", env=self.env)
        self.assertEqual(code, 0, o)
        y = Path(o["config"]).read_text()
        self.assertIn("seed: 42", y)
        self.assertIn("save_every: 100", y)
        self.assertIn("linear: 16", y)

    def test_config_other_trainer_keeps_recipe(self):
        rp = self.make()
        before = rp.read_text()
        code, o = run("config", str(rp), "--trainer", "kohya", env=self.env)
        self.assertEqual(code, 0, o)
        self.assertEqual(rp.read_text(), before)
        self.assertTrue(o["config"].endswith("r.kohya.json"), o)

    def test_rerun_and_diff_same(self):
        rp = self.make()
        code, o = run("rerun", str(rp), "r2", env=self.env)
        self.assertEqual(code, 0, o)
        code, d = run("diff", str(rp), o["recipe"])
        self.assertTrue(d["same_recipe"], d)

    def test_record_scores(self):
        rp = self.make()
        run("record", str(rp), "--score", "judge_win_rate=0.7", "--pick", "step_300", env=self.env)
        r = json.loads(rp.read_text())
        self.assertEqual(r["eval"]["scores"]["judge_win_rate"], 0.7)
        self.assertEqual(r["eval"]["picked"], "step_300")

    def test_run_without_trainer_install_refuses(self):
        rp = self.make()
        code, o = run("run", str(rp), "x.yaml", "--dry", env=self.env)
        self.assertEqual(code, 2)

    def test_leak_finds_terms_and_ips(self):
        repo = self.d / "repo"; repo.mkdir()
        (repo / "a.md").write_text("host " + FAKE_IP + " and SecretName here")
        (repo / "b.md").write_text("localhost 127.0.0.1 fine")
        (self.home / "leak-terms.txt").write_text("secretname\n")
        code, o = run("leak", "--root", str(repo), env=self.env)
        self.assertEqual(code, 2)
        whys = " ".join(h["why"] for h in o["hits"])
        self.assertIn(FAKE_IP, whys)
        self.assertIn("sidecar term", whys)
        self.assertNotIn("127.0.0.1", whys)

    def test_leak_without_terms_refuses(self):
        repo = self.d / "repo"; repo.mkdir()
        code, o = run("leak", "--root", str(repo), env={"TRAINWRIGHT_HOME": str(self.d / "none")})
        self.assertEqual(code, 2)

    def test_loss_at_chance_warns(self):
        rp = self.make()
        code, o = run("record", str(rp), "--score", "eval_loss=10.5", "--vocab", "50257", env=self.env)
        self.assertTrue(any("LOSS-AT-CHANCE" in w for w in o["warn"]), o)
        code, o = run("record", str(rp), "--score", "eval_loss=2.1", env=self.env)
        self.assertEqual(o["warn"], [], o)

    def test_diff_refuses_eval_mismatch(self):
        rp = self.make()
        code, o = run("rerun", str(rp), "r2", env=self.env)
        r2 = Path(o["recipe"])
        for p, w in ((rp, 1024), (r2, 32)):
            r = json.loads(p.read_text()); r["eval"]["window"] = w; r["eval"]["scores"] = {"ppl": 10.0}
            p.write_text(json.dumps(r))
        code, d = run("diff", str(rp), str(r2))
        self.assertEqual(code, 2, d)
        self.assertIn("EVAL-MISMATCH", d["fail"][0])
        r = json.loads(r2.read_text()); r["eval"]["window"] = 1024; r2.write_text(json.dumps(r))
        code, d = run("diff", str(rp), str(r2))
        self.assertEqual(code, 0, d)

    def jsonl(self, name, rows):
        p = self.d / name
        p.write_text("\n".join(json.dumps(r) for r in rows))
        return str(p)

    def test_compare_paired(self):
        a = self.jsonl("a.jsonl", [{"id": i, "correct": i < 250} for i in range(300)])
        b = self.jsonl("b.jsonl", [{"id": i, "correct": i < 200} for i in range(300)])
        code, o = run("compare", "--paired", a, b)
        self.assertEqual((o["only_a_right"], o["only_b_right"]), (50, 0), o)
        self.assertEqual(o["verdict"], "a better")
        self.assertEqual(o["warn"], [])
        b2 = self.jsonl("b2.jsonl", [{"id": i, "correct": i < 247 or i == 299} for i in range(300)])
        code, o = run("compare", "--paired", a, b2, "--pairs", "3")
        self.assertEqual(o["verdict"], "not distinguishable", o)

    def test_compare_small_and_nan(self):
        a = self.jsonl("a.jsonl", [{"id": i, "correct": True} for i in range(20)])
        b = self.jsonl("b.jsonl", [{"id": i, "correct": False} for i in range(20)])
        code, o = run("compare", "--paired", a, b)
        self.assertTrue(o["warn"] and "indicative" in o["warn"][0], o)
        n = self.d / "n.jsonl"; n.write_text('{"id": 1, "correct": true, "logprob": NaN}')
        code, o = run("compare", "--paired", a, str(n))
        self.assertEqual(code, 2)
        self.assertIn("EVAL-NAN", o["fail"][0])


if __name__ == "__main__":
    unittest.main()
