#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Targeted, no-generation replay smoke test; keeps all payloads private."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

def require(condition, message):
    if not condition:
        raise SystemExit("HELD: " + message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def contains(value, wanted):
    if isinstance(value, dict):
        return any(contains(item, wanted) for item in value.values())
    if isinstance(value, list):
        return any(contains(item, wanted) for item in value)
    return isinstance(value, str) and value == wanted

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--pathway", required=True)
parser.add_argument("--pipeline-sha", required=True)
parser.add_argument("--resolver-sha", required=True)
args = parser.parse_args()

os.umask(0o077)
root = args.root.resolve()
out = args.out.resolve()
require(not out.is_relative_to(root), "output must be outside the repository")
out.mkdir(mode=0o700, parents=True, exist_ok=False)

source_path = root / "bin/query_pipeline.py"
source = source_path.read_bytes()
require(sha(source) == args.pipeline_sha, "pipeline identity changed")
require(
    sha((root / "bin/cell_schema.py").read_bytes()) == args.resolver_sha,
    "resolver identity changed",
)
tree = ast.parse(source)
lines = source.decode("utf-8").splitlines(keepends=True)

# Preserve ledger history through the selected accepted result.
ledger_lines = (root / "ledger/query_pathways.jsonl").read_bytes().splitlines(
    keepends=True
)
found = []
for index, line in enumerate(ledger_lines):
    if line.strip():
        record = json.loads(line)
        if record.get("ph") == args.pathway:
            found.append((index, record))
require(len(found) == 1, "target pathway not uniquely present")
index, accepted = found[0]
require(isinstance(accepted.get("answer"), str), "target answer missing")
require(isinstance(accepted.get("question"), str), "target question missing")
ledger = out / "targeted-history.jsonl"
ledger.write_bytes(b"".join(ledger_lines[:index + 1]))

# Find the existing CLI branch that calls find_cached.
modes = []
for node in ast.walk(tree):
    if not isinstance(node, ast.If):
        continue
    test = node.test
    if not (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "MODE"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and isinstance(test.comparators[0].value, str)
    ):
        continue
    calls = {
        child.func.id
        for statement in node.body
        for child in ast.walk(statement)
        if isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
    }
    if "find_cached" in calls:
        require(
            not (calls & {"gen", "seal_append"}),
            "cache branch can generate or append",
        )
        modes.append(test.comparators[0].value)
require(len(modes) == 1, "could not identify one cache-only CLI mode")

# Only the ledger binding and forbidden write/generation entrypoints change.
edits = []
pw_nodes = [
    node for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "PW" for t in node.targets)
]
require(len(pw_nodes) == 1, "PW binding not unique")
node = pw_nodes[0]
edits.append((node.lineno, node.end_lineno, "PW = " + repr(str(ledger)) + "\n"))
for name in ("gen", "seal_append"):
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    require(len(nodes) == 1, "missing protected entrypoint: " + name)
    node = nodes[0]
    edits.append((
        node.lineno, node.end_lineno,
        "def " + name + "(*args, **kwargs):\n"
        "    raise RuntimeError('DISABLED_IN_REPLAY_SMOKE')\n",
    ))

cache_nodes = [
    node for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "find_cached"
]
require(len(cache_nodes) == 1, "find_cached definition not unique")
cache_node = cache_nodes[0]
wrapper = (
    "\n_original_find_cached_for_smoke = find_cached\n"
    "def find_cached(*args, **kwargs):\n"
    "    record = _original_find_cached_for_smoke(*args, **kwargs)\n"
    "    with open(os.environ['OPENROOT_SMOKE_RESULT'], 'w') as destination:\n"
    "        json.dump(record, destination)\n"
    "    return record\n"
)
edits.append((
    cache_node.end_lineno + 1, cache_node.end_lineno, wrapper
))
for start, end, replacement in sorted(edits, reverse=True):
    lines[start - 1:end] = [replacement]
derived = out / "cache-only-pipeline.py"
derived.write_text("".join(lines))
compile(derived.read_bytes(), str(derived), "exec")

launcher = out / "launcher.py"
launcher.write_text("""
import os, pathlib, socket, sqlite3, subprocess, sys
root, derived, mode = sys.argv[1:]
root = pathlib.Path(root)
sys.argv = [str(root / "bin/query_pipeline.py"), mode]
sys.path.insert(0, str(root / "bin"))
import cell_schema
def readonly(*args, **kwargs):
    con = sqlite3.connect(
        (root / "pods/cells.pod.sqlite3").resolve().as_uri() + "?mode=ro",
        uri=True, timeout=5
    )
    con.execute("PRAGMA query_only=ON")
    return con
cell_schema.open_db = readonly
def forbidden(*args, **kwargs):
    raise RuntimeError("NETWORK_OR_SUBPROCESS_DISABLED_IN_REPLAY_SMOKE")
socket.create_connection = forbidden
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
subprocess.Popen = forbidden
namespace = {
    "__name__": "__main__",
    "__file__": str(root / "bin/query_pipeline.py"),
}
exec(compile(pathlib.Path(derived).read_bytes(), derived, "exec"), namespace)
""")

env = os.environ.copy()
env["QPIPE_QUESTION"] = accepted["question"]
for attempt in (1, 2):
    env["OPENROOT_SMOKE_RESULT"] = str(
        out / f"replay-{attempt}.full-result.json"
    )
    result = subprocess.run(
        [
            sys.executable, "-B", str(launcher),
            str(root), str(derived), modes[0],
        ],
        cwd=root, env=env, capture_output=True, timeout=120,
    )
    (out / f"replay-{attempt}.stdout.json").write_bytes(result.stdout)
    (out / f"replay-{attempt}.stderr.txt").write_bytes(result.stderr)
    require(result.returncode == 0,
            f"replay {attempt} failed; inspect private stderr")
    response = json.loads(result.stdout)
    full = json.loads(Path(env["OPENROOT_SMOKE_RESULT"]).read_text())
    require(isinstance(full, dict), "find_cached returned no record")
    require(full.get("ph") == args.pathway,
            "full replay identity differs")
    require(full.get("answer") == accepted["answer"],
            "complete replay answer differs")
    require(contains(response, args.pathway),
            "CLI replay identity differs")
    shown = response.get("sealed_answer", response.get("answer"))
    expected = accepted["answer"]
    require(
        isinstance(shown, str)
        and len(shown) >= min(200, len(expected))
        and expected.startswith(shown),
        "CLI answer display differs from accepted answer",
    )

require(sha(source_path.read_bytes()) == args.pipeline_sha,
        "pipeline changed during smoke test")
report = {
    "status": "TARGETED_REPLAY_SMOKE_PASSED",
    "successful_replays": 2,
    "complete_find_cached_answer": "MATCHED",
    "cli_answer_display": "MATCHED_FULL_OR_PREFIX",
    "pathway_hash": args.pathway,
    "pipeline_sha256": args.pipeline_sha,
    "resolver_sha256": args.resolver_sha,
    "ledger_selection": "preserved history ending at explicit target",
    "database_access": "read-only adapter",
    "generation_and_append_entrypoints": "disabled",
    "child_network_and_subprocesses": "disabled",
    "default_latest_result_selection_tested": False,
    "model_calls": 0,
}
(out / "smoke-result.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
