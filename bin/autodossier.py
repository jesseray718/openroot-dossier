#!/usr/bin/env python3
"""autodossier.py - local AI dossier loop: gather -> generate -> verify -> revise -> seal.

One cycle:
  1. Gather hub context (WORK_LOG tail, manifest, recent git log)
  2. Generate a status dossier via local Ollama (generator model)
  3. Critique via a DIFFERENT model (verifier) - gen != verifier
  4. Revise once from the critique
  5. Emit into corpus/dossiers/<timestamp>.md - sealed by seal_pod on next pass
Env: OLLAMA_URL, GEN_MODEL, VFY_MODEL, OPENROOT
"""
import json, os, subprocess, sys, datetime, urllib.request
from pathlib import Path

OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
GEN = os.environ["GEN_MODEL"]
VFY = os.environ["VFY_MODEL"]
ROOT = Path(os.environ.get("OPENROOT", str(Path.home() / "openroot")))

def chat(model, system, prompt, max_tokens=1024):
    body = json.dumps({"model": model, "stream": False,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": prompt}],
                       "options": {"temperature": 0.4, "num_predict": max_tokens}}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=body,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["message"]["content"]

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT).stdout

def gather(topic=None):
    if topic:
        bp = ROOT / "corpus" / "briefings" / f"{topic}.md"
        if bp.exists():
            return bp.read_text() + "\n\n" + sh("git log --oneline -5")
    # default gathering
    ctx = []
    ctx.append("RECENT COMMITS:\n" + sh("git log --oneline -15"))
    wl = ROOT / "WORK_LOG.md"
    if wl.exists():
        ctx.append("WORK LOG TAIL:\n" + "\n".join(wl.read_text().splitlines()[-10:]))
    man = ROOT / "corpus" / "manifest.jsonl"
    if man.exists():
        lines = man.read_text().strip().splitlines()
        ctx.append(f"CORPUS: {len(lines)} sealed files")
    return "\n\n".join(ctx)

def cycle(topic=None):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ctx = gather(topic)
    sysmsg = ("You are the OpenRoot dossier engine. Output concise, factual dossiers. "
              "Metric: eta = useful_joules / human_joules. Never invent facts; only reflect the context given."
              ) if not topic else (
              "You are the OpenRoot evaluation engine. Reason ONLY from the given brief. "
              "Rank candidates, name the gap each fills, name duplicated layers, give an eta verdict. "
              "Refuse to recommend anything the brief does not support.")
    draft = chat(GEN, sysmsg,
        "You are the OpenRoot dossier engine. Output concise, factual status dossiers. "
        "Metric: eta = useful_joules / human_joules. Never invent facts; only reflect the context given.",
        f"Write a status dossier for OpenRoot based on this context. Sections: STATE, "
        f"WHAT MOVED, RISKS/OPEN THREADS, ETA ASSESSMENT. Context:\n\n{ctx}")
    critique = chat(VFY,
        "You are a strict verifier of engineering dossiers. Find fabrications, "
        "unsupported claims, and missing risks. Be terse and concrete.",
        f"Critique this dossier against the context. List concrete defects only.\n\n"
        f"CONTEXT:\n{ctx}\n\nDOSSIER:\n{draft}")
    revised = chat(GEN,
        "You are the OpenRoot dossier engine. Apply the verifier's critique honestly. "
        "Where the critique flags something unsupported, remove or qualify it.",
        f"Original:\n{draft}\n\nVerifier critique:\n{critique}\n\nProduce the corrected final dossier.")
    out = ROOT / "corpus" / "dossiers"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"dossier-{topic if topic else ''}-{ts}.md"
    path.write_text(
        f"# Autodossier {ts}\n"
        f"generator: {GEN} | verifier: {VFY} | revision cycle: 1\n\n"
        f"## Verifier critique (applied)\n{critique}\n\n{revised}\n")
    print(f"CYCLE {ts}: dossier written -> {path}")
    return path

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ask":
        cycle(sys.argv[2]); sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        cycle(); sys.exit(0)
    interval = int(os.environ.get("DOSSIER_INTERVAL", "3600"))
    print(f"LOOP: one dossier cycle every {interval}s. Ctrl-C to stop.")
    while True:
        try:
            cycle()
        except Exception as e:
            print(f"cycle failed: {e}")
        import time
        time.sleep(interval)
