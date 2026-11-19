"""Verify the trainwright wiki examples against tw.py at v0.1.0.

Runs every page example in a fresh temp folder with a throwaway TRAINWRIGHT_HOME,
prints each command and its output with the temp folder masked as <tmp>.
Usage: python ai-docs/notes/2026-11-19-wiki-verify.py > ai-docs/notes/2026-11-19-wiki-verify.out.txt
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

TW = Path(__file__).resolve().parents[2] / "skills" / "trainwright" / "scripts" / "tw.py"
tmp = Path(tempfile.mkdtemp(prefix="twwiki-"))
home = tmp / "home"
home.mkdir()
(home / "hosts.json").write_text(json.dumps({
    "disk_floor_gb": 1,
    "trainers": {"ai-toolkit": {"python": "/opt/ai-toolkit/venv/bin/python", "entry": "/opt/ai-toolkit/run.py"}}}))
(home / "leak-terms.txt").write_text("# one private term per line\nsecret-host-name\n")
env = dict(os.environ, TRAINWRIGHT_HOME=str(home))


def tw(label, *args):
    p = subprocess.run([sys.executable, str(TW), *args], cwd=tmp, env=env, capture_output=True, text=True)
    text = (p.stdout + p.stderr).replace(str(tmp).replace("\\", "\\\\"), "<tmp>").replace(str(tmp), "<tmp>")
    print(f"=== {label}\n$ python tw.py {' '.join(args)}\n{text.rstrip()}\nexit {p.returncode}\n")


def edit(name, fn):
    p = tmp / name
    r = json.loads(p.read_text())
    fn(r)
    p.write_text(json.dumps(r, indent=1) + "\n")


# fixtures: a stand-in base file and a two-image dataset with captions
(tmp / "base.safetensors").write_bytes(b"stand-in base weights")
ds = tmp / "datasets" / "my-style"
ds.mkdir(parents=True)
for i in (1, 2):
    (ds / f"img{i}.png").write_bytes(b"png%d" % i)
    (ds / f"img{i}.txt").write_text(f"mystyle, picture {i}")

tw("new", "new", "image-lora", "my-style")
tw("new-exists", "new", "image-lora", "my-style")
tw("new-badkind", "new", "audio", "x")
tw("check-empty", "check", "my-style.recipe.json", "--shallow")
tw("hash-base", "hash", "base.safetensors")
tw("hash-manifest", "hash", "datasets/my-style", "--manifest", "--source", "own photos")


def fill(r):
    r["base"].update(name="Example base 1.0", path=str(tmp / "base.safetensors"), arch="example",
                     licence="apache-2.0",
                     sha256=__import__("hashlib").sha256(b"stand-in base weights").hexdigest())
    m = json.loads(subprocess.run([sys.executable, str(TW), "hash", "datasets/my-style", "--manifest",
                                   "--source", "own photos"], cwd=tmp, env=env, capture_output=True, text=True).stdout)
    r["dataset"].update(root=str(ds), items=m["items"])
    r["config"]["trigger"] = "mystyle"
    r["output"]["dir"] = str(tmp / "output" / "my-style")


edit("my-style.recipe.json", fill)
tw("check-clean", "check", "my-style.recipe.json", "--shallow")
tw("config", "config", "my-style.recipe.json", "--trainer", "ai-toolkit")
print("=== config-yaml\n" + (tmp / "my-style.recipe.yaml").read_text().replace(str(tmp).replace("\\", "\\\\"), "<tmp>").replace(str(tmp).replace("\\", "/"), "<tmp>").rstrip() + "\n")
tw("config-kohya-out", "config", "my-style.recipe.json", "--trainer", "kohya", "--out", "my-style.kohya.json")
# known issue in 0.1.0: without --out, a non-ai-toolkit config is written over the recipe itself
(tmp / "copy.recipe.json").write_text((tmp / "my-style.recipe.json").read_text())
tw("config-kohya-overwrite", "config", "copy.recipe.json", "--trainer", "kohya")
print("=== config-kohya-overwrite-keys\n" + ", ".join(json.loads((tmp / "copy.recipe.json").read_text())) + "\n")
tw("run-dry", "run", "my-style.recipe.json", "my-style.recipe.yaml", "--dry")

# gates that refuse
edit("my-style.recipe.json", lambda r: r.update(use="sellable") or r["base"].update(licence="cc-by-nc-4.0"))
tw("check-nc", "check", "my-style.recipe.json", "--shallow")
edit("my-style.recipe.json", lambda r: r.update(use="personal") or r["base"].update(licence="apache-2.0")
     or r["dataset"].update(subject="a friend"))
tw("check-consent", "check", "my-style.recipe.json", "--shallow")
edit("my-style.recipe.json", lambda r: r["dataset"].update(consent="granted:2026-11-01 the friend"))
(ds / "img1.txt").write_text("mystyle, picture 1")
(tmp / "output" / "my-style").mkdir(parents=True)
(tmp / "output" / "my-style" / "step_100.safetensors").write_bytes(b"x")
tw("check-collision", "check", "my-style.recipe.json", "--shallow")

tw("record", "record", "my-style.recipe.json", "--score", "style_match=0.82", "--score", "note=best at 300",
   "--pick", "step_300", "--files", "output/my-style/step_100.safetensors")
tw("rerun", "rerun", "my-style.recipe.json", "my-style-r2")
edit("my-style-r2.recipe.json", lambda r: r["config"].update(lr=5e-5))
tw("diff", "diff", "my-style.recipe.json", "my-style-r2.recipe.json")

# leak scan on a tiny folder (no git)
rep = tmp / "repo"
rep.mkdir()
(rep / "README.md").write_text("Runs next to secret-host-name.\n")
(rep / "lora.safetensors").write_bytes(b"x")
tw("leak", "leak", "--root", "repo")
(home / "leak-terms.txt").unlink()
tw("leak-noterms", "leak", "--root", "repo")
tw("leak-allow", "leak", "--root", "repo", "--allow-no-terms")
