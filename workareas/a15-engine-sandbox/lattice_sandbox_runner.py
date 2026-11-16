#!/usr/bin/env python3
"""Sandboxed runner for A15 lattice_cli.py.

Read-only against the live OpenRoot tree. All writes remain inside
workareas/a15-engine-sandbox. Does not execute the original A15 script.
"""
import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LIVE_ROOT=Path('/home/jesse/openroot').resolve()

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--task',required=True)
    ap.add_argument('--approve-write',action='store_true')
    args=ap.parse_args()

    task=Path(args.task).resolve()
    if not task.is_file():
        print('ERROR: task file not found',file=sys.stderr); return 2
    if str(task).startswith(str(LIVE_ROOT)+'/') and 'a15-engine-sandbox' not in str(task):
        print('ERROR: task file must be inside sandbox',file=sys.stderr); return 2

    original=Path('workareas/archive-extract-test/extract-YTyNf6HR/0015_lattice_cli.py').resolve()
    if not original.is_file():
        print('ERROR: A15 source not found',file=sys.stderr); return 2

    receipt={
      'timestamp':datetime.now(timezone.utc).isoformat(),
      'tool':'lattice_sandbox_runner_v1',
      'original_a15_sha256':sha256(original),
      'task_sha256':sha256(task),
      'sandbox_root':str(ROOT),
      'live_root':str(LIVE_ROOT),
      'approve_write':args.approve_write,
      'execution_status':'not_executed_static_wrapper'
    }
    out=ROOT/'lattice_sandbox_receipt.json'
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(out)
    print(json.dumps(receipt,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
