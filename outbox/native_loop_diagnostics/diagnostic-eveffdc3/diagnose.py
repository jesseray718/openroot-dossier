
import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path

out = Path(__file__).resolve().parent
repo = Path.home() / "openroot"
control = Path.home() / ".local/state/openroot-foundation-repairs"
control.mkdir(parents=True, exist_ok=True)

lock = (control / "native-diagnostic.lock").open("w")
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("Another native diagnostic is active; no duplicate started.", flush=True)
    raise SystemExit(0)

boot = """
import faulthandler, runpy, sys
script = sys.argv[1]
sys.argv = sys.argv[1:]
print("PYTHON_STARTED:", script, flush=True)
faulthandler.enable()
faulthandler.dump_traceback_later(30, repeat=True)
runpy.run_path(script, run_name="__main__")
"""

env = dict(os.environ)
env.update(
    PYTHONUNBUFFERED="1",
    MODELS_TRY="qwen2.5:7b",
    NQ="1"
)

results = []
for name, seconds in (
    ("question_travel_v1.py", 600),
    ("pods_fractal_v1.py", 300),
):
    print("\nSTART:", name, flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-u", "-c", boot,
             str(out / name), str(out)],
            cwd=repo, env=env,
            stdin=subprocess.DEVNULL,
            stdout=sys.stdout,
            stderr=subprocess.STDOUT,
            timeout=seconds
        )
        record = {"step": name, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        record = {"step": name, "status": "TIME_LIMIT_REACHED",
                  "seconds": seconds}

    results.append(record)
    (out / "diagnostic-results.json").write_text(
        json.dumps(results, indent=2)
    )
    print("RESULT:", json.dumps(record), flush=True)

print("\nNATIVE_DIAGNOSTIC_FINISHED", flush=True)
