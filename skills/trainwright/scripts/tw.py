#!/usr/bin/env python3
"""trainwright: training runs as rerunnable recipe records (standard library only).

Verbs: new, check, config, run, record, rerun, diff, leak, hash.
Every verb prints JSON. Exit 0 ok, 2 a gate refused (reasons listed), 1 usage error.
Private facts (trainer paths, hosts, leak terms) come from TRAINWRIGHT_HOME.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KINDS = ("image-lora", "video-lora", "voice", "llm")
TRAINERS = {
    "image-lora": ["ai-toolkit", "musubi-tuner", "kohya"],
    "video-lora": ["musubi-tuner", "ai-toolkit"],
    "voice": ["voxcpm"],
    "llm": ["unsloth", "trl"],
}
NONCOMMERCIAL = re.compile(r"(?i)\b(nc|non-?commercial|cc[- ]by[- ]nc|research[- ]only|personal[- ]use)\b")
SELLABLE_BANNED = re.compile(r"(?i)krea[ _-]?2")
META_GATED = re.compile(r"(?i)\b(llama|sam[ _-]?3|meta-)")
CONSENT_OK = re.compile(r"^(self|granted:\d{4}-\d{2}-\d{2}.*|public-domain|licensed:.+|synthetic)$")
MEDIA_EXT = {".safetensors", ".gguf", ".ckpt", ".pt", ".bin", ".wav", ".mp3", ".flac",
             ".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"}
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
IP_OK = {"127.0.0.1", "0.0.0.0"}


def out(obj, code=0):
    print(json.dumps(obj, indent=1))
    sys.exit(code)


def home():
    h = os.environ.get("TRAINWRIGHT_HOME")
    return Path(h) if h else Path.home() / ".trainwright"


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def save_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1) + "\n", encoding="utf-8", newline="\n")


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def hosts():
    p = home() / "hosts.json"
    return load_json(p) if p.exists() else {}


# ---------- new ----------
def skeleton(kind, name):
    return {
        "trainwright": 1,
        "name": name,
        "kind": kind,
        "use": "personal",  # personal | sellable | public-release
        "trainer": {"name": TRAINERS[kind][0], "version": ""},
        "base": {"name": "", "path": "", "arch": "", "sha256": "", "licence": "", "gated": False},
        "dataset": {"root": "", "items": [], "captions": "", "subject": "",
                    "consent": "", "licence": ""},
        "config": {"rank": 16, "alpha": 16, "lr": 1e-4, "steps": 1000, "batch": 1,
                   "resolution": 1024, "save_every": 100, "seed": 42,
                   "quant": "qfloat8", "low_vram": True, "trigger": ""},
        "eval": {"sheet": [], "strengths": [0.0, 0.6, 0.8, 1.0], "judge": "artwright-judge",
                 "scores": {}, "picked": ""},
        "runs": [],
        "output": {"dir": "", "files": []},
    }


def cmd_new(a):
    if a.kind not in KINDS:
        out({"ok": False, "error": f"kind must be one of {KINDS}"}, 1)
    p = Path(a.out or f"{a.name}.recipe.json")
    if p.exists() and not a.force:
        out({"ok": False, "error": f"{p} exists; pick a new name or --force"}, 1)
    r = skeleton(a.kind, a.name)
    if a.kind == "llm":
        r["config"].update({"rank": 16, "lr": 2e-4, "steps": 500, "resolution": None,
                            "quant": "4bit", "max_seq_len": 2048})
        r["eval"].update({"strengths": [], "judge": "lm-eval or held-out prompt sheet"})
    if a.kind == "voice":
        r["config"].update({"resolution": None, "batch": 2, "grad_accum": 8})
        r["eval"].update({"strengths": [], "judge": "voicewright check + human listen"})
    if a.kind == "video-lora":
        r["config"].update({"resolution": 512, "frames": 33, "block_swap": 20})
    save_json(p, r)
    out({"ok": True, "recipe": str(p), "next": "fill base, dataset, then tw.py check"})


# ---------- check ----------
def gpu_state():
    try:
        s = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
        u, used, tot = [int(x.strip()) for x in s.stdout.strip().splitlines()[0].split(",")]
        return {"util": u, "used_mb": used, "total_mb": tot}
    except Exception:
        return None


def gates(r, recipe_path, deep=True):
    fail, warn = [], []
    use = r.get("use", "personal")
    base = r.get("base", {})
    ds = r.get("dataset", {})
    for k in ("name", "path", "licence"):
        if not base.get(k):
            fail.append(f"base.{k} is empty")
    if not base.get("sha256"):
        fail.append("base.sha256 is empty (tw.py hash <file>)")
    lic_all = " ".join([base.get("licence", ""), ds.get("licence", "")])
    if use in ("sellable", "public-release") and NONCOMMERCIAL.search(lic_all):
        fail.append(f"licence '{lic_all.strip()}' is non-commercial; the trained model inherits it and cannot be {use}")
    if use == "sellable" and SELLABLE_BANNED.search(base.get("name", "") + base.get("path", "")):
        fail.append("Krea 2 base is never used in a sellable project")
    if META_GATED.search(base.get("name", "")) or base.get("gated"):
        warn.append("gated base (Meta or similar): use an ungated base unless a measured gain justifies it")
    # dataset
    items = ds.get("items", [])
    if not items:
        fail.append("dataset.items is empty (tw.py hash --manifest <folder> fills it)")
    if ds.get("subject") and not CONSENT_OK.match(ds.get("consent", "")):
        fail.append(f"dataset subject '{ds['subject']}' has no consent record "
                    "(self | granted:YYYY-MM-DD <who> | public-domain | licensed:<terms> | synthetic)")
    if r.get("kind") == "voice" and not ds.get("subject"):
        fail.append("voice dataset needs dataset.subject (whose voice) and consent")
    for it in items:
        if not it.get("source"):
            fail.append(f"dataset item {it.get('file')} has no source")
            break
    if deep and ds.get("root"):
        root = Path(ds["root"])
        bad = [it["file"] for it in items if (root / it["file"]).exists()
               and it.get("sha256") and sha256(root / it["file"]) != it["sha256"]]
        missing = [it["file"] for it in items if not (root / it["file"]).exists()]
        if bad:
            fail.append(f"{len(bad)} dataset files changed since the manifest: {bad[:3]}")
        if missing:
            fail.append(f"{len(missing)} dataset files missing: {missing[:3]}")
    # config
    c = r.get("config", {})
    if "seed" not in c:
        fail.append("config.seed missing: a run without a seed cannot be repeated")
    if r.get("kind") in ("image-lora", "video-lora") and c.get("save_every", 0) > 250:
        warn.append("save_every > 250: style LoRAs often peak early; save every 100 and pick by eye")
    if r.get("kind") in ("image-lora", "video-lora") and 0.0 not in r.get("eval", {}).get("strengths", []):
        fail.append("eval.strengths lacks 0.0: every strength sweep needs a strength-0 control")
    # output collision (ai-toolkit silently resumes a same-name run)
    od = r.get("output", {}).get("dir")
    if od and Path(od).exists() and any(Path(od).iterdir()):
        fail.append(f"output.dir {od} is not empty: trainers like ai-toolkit resume a same-name run silently; use a new name")
    # host
    if deep:
        g = gpu_state()
        if g and (g["util"] > 10 or g["used_mb"] > 6000):
            warn.append(f"GPU busy ({g['util']}% load, {g['used_mb']} MB): queue behind it, never stop the other job")
        floor = float(hosts().get("disk_floor_gb", 100))
        target = Path(od) if od else Path(recipe_path).resolve().parent
        probe = target
        while not probe.exists() and probe.parent != probe:
            probe = probe.parent
        try:
            free = shutil.disk_usage(probe).free / 1e9
            if free < floor:
                fail.append(f"{probe} has {free:.0f} GB free, under the {floor:.0f} GB floor")
        except OSError:
            pass
    return fail, warn


def cmd_check(a):
    r = load_json(a.recipe)
    fail, warn = gates(r, a.recipe, deep=not a.shallow)
    out({"ok": not fail, "fail": fail, "warn": warn}, 2 if fail else 0)


# ---------- hash ----------
def cmd_hash(a):
    p = Path(a.path)
    if a.manifest:
        exts = {".png", ".jpg", ".jpeg", ".webp", ".wav", ".flac", ".mp3", ".mp4", ".txt", ".jsonl"}
        items = []
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in exts:
                items.append({"file": f.relative_to(p).as_posix(), "sha256": sha256(f),
                              "source": a.source or ""})
        out({"ok": True, "root": str(p), "count": len(items), "items": items})
    out({"ok": True, "file": str(p), "sha256": sha256(p)})


# ---------- config ----------
def yaml_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    return json.dumps(s)


def to_yaml(obj, ind=0):
    sp = "  " * ind
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{sp}{k}:")
                lines.append(to_yaml(v, ind + 1))
            else:
                lines.append(f"{sp}{k}: {yaml_scalar(v) if not isinstance(v, (dict, list)) else ('{}' if isinstance(v, dict) else '[]')}")
    else:
        for v in obj:
            if isinstance(v, dict):
                first = True
                for line in to_yaml(v, ind + 1).splitlines():
                    lines.append((f"{sp}- " + line.strip()) if first else line)
                    first = False
            else:
                lines.append(f"{sp}- {yaml_scalar(v)}")
    return "\n".join(lines)


def aitoolkit_config(r):
    c, b, d = r["config"], r["base"], r["dataset"]
    is_video = r["kind"] == "video-lora"
    proc = {
        "type": "sd_trainer",
        "training_folder": str(Path(r["output"]["dir"]).parent.as_posix()) if r["output"].get("dir") else "output",
        "device": "cuda:0",
        "trigger_word": c.get("trigger") or None,
        "network": {"type": "lora", "linear": c["rank"], "linear_alpha": c.get("alpha", c["rank"])},
        "save": {"dtype": "float16", "save_every": c["save_every"], "max_step_saves_to_keep": 50},
        "datasets": [{"folder_path": d["root"], "caption_ext": "txt", "caption_dropout_rate": 0.05,
                      "resolution": [c["resolution"]] if c.get("resolution") else [512]}],
        "train": {"batch_size": c["batch"], "steps": c["steps"], "gradient_accumulation_steps": c.get("grad_accum", 1),
                  "train_unet": True, "train_text_encoder": False, "gradient_checkpointing": True,
                  "noise_scheduler": c.get("noise_scheduler", "flowmatch"), "optimizer": "adamw8bit", "lr": c["lr"],
                  "dtype": "bf16", "seed": c["seed"], "disable_sampling": bool(c.get("disable_sampling"))},
        "model": {"name_or_path": b["path"], "quantize": bool(c.get("quant")),
                  "qtype": c.get("quant") or "qfloat8", "quantize_te": bool(c.get("quant")),
                  "qtype_te": c.get("quant") or "qfloat8", "low_vram": bool(c.get("low_vram"))},
        "sample": {"sampler": c.get("noise_scheduler", "flowmatch"), "sample_every": c["save_every"], "width": c.get("resolution") or 512,
                   "height": c.get("resolution") or 512, "seed": c["seed"], "walk_seed": False,
                   "prompts": [p if isinstance(p, str) else p.get("prompt", "") for p in r["eval"].get("sheet", [])][:6] or ["a photo"]},
    }
    if b.get("arch"):
        proc["model"]["arch"] = b["arch"]
        proc["train"]["timestep_type"] = c.get("timestep_type", "weighted")
    if c.get("sample_steps"):
        proc["sample"]["sample_steps"] = c["sample_steps"]
        proc["sample"]["guidance_scale"] = c.get("guidance", 4.0)
    if is_video:
        proc["datasets"][0]["num_frames"] = c.get("frames", 33)
    return {"job": "extension", "config": {"name": r["name"], "process": [proc]},
            "meta": {"name": r["name"], "version": "1.0", "trainwright_recipe": True}}


def cmd_config(a):
    r = load_json(a.recipe)
    t = a.trainer or r["trainer"]["name"]
    stem = Path(a.recipe).name
    for suf in (".recipe.json", ".json"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            break
    outp = Path(a.out) if a.out else Path(a.recipe).parent / f"{stem}.{t}"
    if t == "ai-toolkit":
        text = to_yaml(aitoolkit_config(r)) + "\n"
        outp = outp if a.out else outp.with_name(outp.name + ".yaml")
        outp.write_text(text, encoding="utf-8", newline="\n")
        proven = True
    else:
        # Other trainers: a neutral JSON of the settings; the reference for that kind maps it to flags.
        outp = outp if a.out else outp.with_name(outp.name + ".json")
        if outp.resolve() == Path(a.recipe).resolve():
            out({"ok": False, "error": "config output would overwrite the recipe; pass --out"}, 1)
        save_json(outp, {"trainer": t, "base": r["base"]["path"], "dataset": r["dataset"]["root"], **r["config"]})
        proven = False
    out({"ok": True, "trainer": t, "config": str(outp), "proven_on_real_trainer": proven,
         "note": None if proven else "unproven mapping: run a dry run of a few steps before trusting it"})


# ---------- run ----------
def trainer_cmd(r, cfg):
    h = hosts().get("trainers", {})
    t = r["trainer"]["name"]
    ent = h.get(t)
    if not ent:
        return None, f"no install for trainer '{t}' in {home() / 'hosts.json'} (trainers.{t}.python and .entry)"
    return [ent["python"], ent["entry"], str(Path(cfg).resolve())], None


def cmd_run(a):
    r = load_json(a.recipe)
    fail, warn = gates(r, a.recipe, deep=True)
    if fail and not a.dry:
        out({"ok": False, "fail": fail, "warn": warn}, 2)
    cmd, err = trainer_cmd(r, a.config)
    if err:
        out({"ok": False, "fail": [err]}, 2)
    entry = {"started": dt.datetime.now().isoformat(timespec="seconds"), "dry": a.dry, "cmd": cmd,
             "steps": a.steps if a.dry else r["config"]["steps"]}
    if a.dry:
        out({"ok": True, "dry": True, "would_run": cmd, "fail": fail, "warn": warn,
             "note": "dry run: set config.steps to a few steps in a copy and run that as the smoke test"})
    log = Path(a.recipe).with_suffix(".log")
    with open(log, "w", encoding="utf-8") as lf:
        p = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=Path(cmd[1]).parent)
    entry.update({"ended": dt.datetime.now().isoformat(timespec="seconds"), "exit": p.returncode, "log": str(log)})
    r.setdefault("runs", []).append(entry)
    save_json(a.recipe, r)
    out({"ok": p.returncode == 0, "run": entry}, 0 if p.returncode == 0 else 2)


# ---------- record ----------
def cmd_record(a):
    r = load_json(a.recipe)
    if a.score:
        for s in a.score:
            k, v = s.split("=", 1)
            r["eval"]["scores"][k] = float(v) if re.fullmatch(r"-?\d+(\.\d+)?", v) else v
    if a.pick:
        r["eval"]["picked"] = a.pick
    if a.files:
        r["output"]["files"] = [{"file": f, "sha256": sha256(f)} for f in a.files]
    if a.vocab:
        r["eval"]["vocab"] = a.vocab
    save_json(a.recipe, r)
    missing = [k for k in ("picked",) if not r["eval"].get(k)]
    if not r["eval"]["scores"]:
        missing.append("scores")
    warn = []
    v = r["eval"].get("vocab")
    for k in ("eval_loss", "loss"):
        loss = r["eval"]["scores"].get(k)
        if v and isinstance(loss, float):
            chance = math.log(int(v))
            if loss >= 0.9 * chance:
                warn.append(f"LOSS-AT-CHANCE: {k} {loss} >= 0.9 x ln({v}) = {0.9 * chance:.2f}; "
                            "nothing learned, or labels or template broken")
            break
    out({"ok": True, "recipe": a.recipe, "still_missing": missing, "warn": warn})


# ---------- rerun ----------
def cmd_rerun(a):
    r = load_json(a.recipe)
    n = dict(r)
    n["name"] = a.name
    n["runs"] = []
    n["eval"] = dict(r["eval"], scores={}, picked="")
    n["output"] = {"dir": str(Path(r["output"].get("dir") or ".").parent / a.name) if r["output"].get("dir") else "", "files": []}
    n["rerun_of"] = {"name": r["name"], "recipe": str(a.recipe)}
    p = Path(a.recipe).parent / f"{a.name}.recipe.json"
    if p.exists():
        out({"ok": False, "error": f"{p} exists"}, 1)
    save_json(p, n)
    fail, warn = gates(n, p, deep=True)
    out({"ok": not fail, "recipe": str(p), "fail": fail, "warn": warn,
         "note": "same seed, config and dataset hashes; compare with tw.py diff after the run"}, 2 if fail else 0)


# ---------- diff ----------
def flat(o, pre=""):
    if isinstance(o, dict):
        d = {}
        for k, v in o.items():
            d.update(flat(v, f"{pre}{k}."))
        return d
    return {pre.rstrip("."): o}


def cmd_diff(a):
    x, y = flat(load_json(a.a)), flat(load_json(a.b))
    mm = {k: [x.get(k), y.get(k)] for k in EVAL_SETUP if x.get(k) != y.get(k)}
    if mm and (load_json(a.a)["eval"].get("scores") or load_json(a.b)["eval"].get("scores")):
        out({"ok": False, "fail": ["EVAL-MISMATCH: scores were measured on a different eval setup; "
                                   "rerun both with the same tokens, window, stride and tokenizer"],
             "eval_setup_differences": mm}, 2)
    skip = re.compile(r"^(name|runs|output|rerun_of|eval\.scores|eval\.picked)")
    keys = sorted(set(x) | set(y))
    d = {k: [x.get(k), y.get(k)] for k in keys if not skip.match(k) and x.get(k) != y.get(k)}
    sx, sy = load_json(a.a)["eval"].get("scores", {}), load_json(a.b)["eval"].get("scores", {})
    sd = {k: [sx.get(k), sy.get(k)] for k in sorted(set(sx) | set(sy))}
    out({"ok": True, "same_recipe": not d, "recipe_differences": d, "scores": sd})


EVAL_SETUP = ("eval.window", "eval.stride", "eval.tokens_hash", "eval.tokenizer", "eval.decode")


# ---------- compare ----------
def load_items(p):
    items, nan = {}, 0
    for n, line in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        o = json.loads(line)
        nan += any(isinstance(v, float) and math.isnan(v) for v in o.values())
        items[str(o.get("id", n))] = bool(o["correct"])
    return items, nan


def mcnemar_p(b, c):
    """Exact two-sided McNemar: binomial(b + c, 0.5) on the disagreements."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def cmd_compare(a):
    xa, na = load_items(a.a)
    xb, nb = load_items(a.b)
    if na or nb:
        out({"ok": False, "fail": [f"EVAL-NAN: NaN values in results ({na} in a, {nb} in b); "
                                   "score with log_softmax, not a hand-written softmax"]}, 2)
    ids = sorted(set(xa) & set(xb))
    if not ids:
        out({"ok": False, "fail": ["no shared item ids"]}, 2)
    b = sum(xa[i] and not xb[i] for i in ids)
    c = sum(xb[i] and not xa[i] for i in ids)
    pv = mcnemar_p(b, c)
    thr = 0.05 / max(1, a.pairs)
    warn = [] if len(ids) >= 200 else [f"only {len(ids)} items: any ranking is indicative; a blind human pass decides"]
    if set(xa) != set(xb):
        warn.append(f"{len(set(xa) ^ set(xb))} items in only one file were left out")
    out({"ok": True, "items": len(ids), "acc_a": round(sum(xa[i] for i in ids) / len(ids), 4),
         "acc_b": round(sum(xb[i] for i in ids) / len(ids), 4), "only_a_right": b, "only_b_right": c,
         "p": round(pv, 6), "threshold": thr,
         "verdict": ("a better" if b > c else "b better") if pv < thr else "not distinguishable", "warn": warn})


# ---------- leak ----------
def tracked_files(root):
    try:
        s = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True)
        return [root / f for f in s.stdout.splitlines()]
    except Exception:
        return [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


def leak_terms():
    for p in (home() / "leak-terms.txt", Path.home() / ".trainwright" / "leak-terms.txt"):
        if p.exists():
            return [t.strip() for t in p.read_text(encoding="utf-8").splitlines()
                    if t.strip() and not t.startswith("#")], str(p)
    return None, None


def cmd_leak(a):
    root = Path(a.root).resolve()
    terms, src = leak_terms()
    if terms is None and not a.allow_no_terms:
        out({"ok": False, "fail": ["no leak-terms.txt in TRAINWRIGHT_HOME: the scan would prove nothing"]}, 2)
    hits = []
    for f in tracked_files(root):
        if not f.exists():
            continue
        rel = f.relative_to(root).as_posix()
        if f.suffix.lower() in MEDIA_EXT and not rel.startswith(".github/images/"):
            hits.append({"file": rel, "why": "media or weights file"})
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for ip in IPV4.findall(text):
            if ip not in IP_OK and all(0 <= int(p) <= 255 for p in ip.split(".")) and not ip.startswith("0."):
                hits.append({"file": rel, "why": f"IP address {ip}"})
        low = text.lower()
        for t in terms or []:
            if t.lower() in low:
                hits.append({"file": rel, "why": f"sidecar term #{(terms.index(t) + 1)}"})
    out({"ok": not hits, "terms_from": src, "hits": hits}, 2 if hits else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tw.py")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("new"); p.add_argument("kind"); p.add_argument("name"); p.add_argument("--out"); p.add_argument("--force", action="store_true"); p.set_defaults(f=cmd_new)
    p = sp.add_parser("check"); p.add_argument("recipe"); p.add_argument("--shallow", action="store_true"); p.set_defaults(f=cmd_check)
    p = sp.add_parser("hash"); p.add_argument("path"); p.add_argument("--manifest", action="store_true"); p.add_argument("--source"); p.set_defaults(f=cmd_hash)
    p = sp.add_parser("config"); p.add_argument("recipe"); p.add_argument("--trainer"); p.add_argument("--out"); p.set_defaults(f=cmd_config)
    p = sp.add_parser("run"); p.add_argument("recipe"); p.add_argument("config"); p.add_argument("--dry", action="store_true"); p.add_argument("--steps", type=int, default=5); p.set_defaults(f=cmd_run)
    p = sp.add_parser("record"); p.add_argument("recipe"); p.add_argument("--score", action="append"); p.add_argument("--pick"); p.add_argument("--files", nargs="*"); p.add_argument("--vocab", type=int); p.set_defaults(f=cmd_record)
    p = sp.add_parser("compare"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--paired", action="store_true"); p.add_argument("--pairs", type=int, default=1); p.set_defaults(f=cmd_compare)
    p = sp.add_parser("rerun"); p.add_argument("recipe"); p.add_argument("name"); p.set_defaults(f=cmd_rerun)
    p = sp.add_parser("diff"); p.add_argument("a"); p.add_argument("b"); p.set_defaults(f=cmd_diff)
    p = sp.add_parser("leak"); p.add_argument("--root", default="."); p.add_argument("--allow-no-terms", action="store_true"); p.set_defaults(f=cmd_leak)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
