"""trainwright job node: runs a training job on the ComfyUI queue so training waits its turn on the GPU.

A job file is JSON: {"name": str, "log": path, "steps": [{"cwd": path, "cmd": [argv...], "env": {..}}]}.
Steps run in order; any non-zero exit fails the node. ComfyUI models are unloaded first so the trainer gets the VRAM.
"""
import json
import os
import subprocess
import time

import comfy.model_management as mm


class TrainwrightJob:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"job_file": ("STRING", {"default": "path/to/job.json"})}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("log_tail",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "trainwright"

    @classmethod
    def IS_CHANGED(cls, job_file):
        return time.time()  # always rerun when queued

    def run(self, job_file):
        with open(job_file, encoding="utf-8") as f:
            job = json.load(f)
        mm.unload_all_models()
        mm.soft_empty_cache()
        log_path = job.get("log") or os.path.splitext(job_file)[0] + ".log"
        with open(log_path, "a", encoding="utf-8", errors="replace") as log:
            log.write(f"\n=== {job.get('name', job_file)} start {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for i, step in enumerate(job["steps"]):
                env = dict(os.environ)
                env.update(step.get("env", {}))
                env["PYTHONIOENCODING"] = "utf-8"
                log.write(f"--- step {i}: {' '.join(step['cmd'])}\n")
                log.flush()
                t0 = time.time()
                rc = subprocess.call(step["cmd"], cwd=step.get("cwd"), env=env, stdout=log, stderr=subprocess.STDOUT)
                log.write(f"--- step {i} exit {rc} in {time.time() - t0:.0f}s\n")
                log.flush()
                if rc != 0:
                    raise RuntimeError(f"trainwright job {job.get('name')} step {i} exited {rc}; log {log_path}")
            log.write(f"=== done {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        with open(log_path, encoding="utf-8", errors="replace") as f:
            tail = f.read()[-3000:]
        return {"ui": {"text": [tail]}, "result": (tail,)}


NODE_CLASS_MAPPINGS = {"TrainwrightJob": TrainwrightJob}
NODE_DISPLAY_NAME_MAPPINGS = {"TrainwrightJob": "trainwright job (runs a training recipe)"}
