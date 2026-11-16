#!/usr/bin/env python3
"""OpenRoot-compatible sandboxed lattice evaluator v1.

Reads one explicit sandbox task JSON file, applies explicit rules,
computes a proof trace and Merkle root, and writes only sandbox artifacts.
It never touches the live OpenRoot tree.
"""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

SANDBOX=Path(__file__).resolve().parent
LEDGER=SANDBOX/'acre/ledger.jsonl'
LIVE_ROOT=Path('/home/jesse/openroot').resolve()
RULES_VERSION='lattice-rules-v1'

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_hash(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
    ).hexdigest()

def merkle_root(items):
    if not items:
        return hashlib.sha256(b'empty').hexdigest()
    layer=[canonical_hash(x) for x in items]
    while len(layer)>1:
        if len(layer)%2:
            layer.append(layer[-1])
        layer=[
            hashlib.sha256((layer[i]+layer[i+1]).encode()).hexdigest()
            for i in range(0,len(layer),2)
        ]
    return layer[0]

def evaluate(task):
    trace=[]
    eta=float(task.get('base_eta',55.0))

    if task.get('observation_days',0)<7:
        trace.append({
            'rule':'R001',
            'effect':'eta_penalty',
            'amount':6,
            'reason':'insufficient observation'
        })
        eta-=6

    if not task.get('feedback',False):
        trace.append({
            'rule':'R002',
            'effect':'eta_penalty',
            'amount':8,
            'reason':'no feedback mechanism'
        })
        eta-=8

    if task.get('involves_compute',False) and not task.get('compute_joules',0):
        trace.append({
            'rule':'R003',
            'effect':'eta_penalty',
            'amount':6,
            'reason':'compute without energy accounting'
        })
        eta-=6

    eta=max(0.0,min(100.0,eta))
    return {
        'eta_score':eta,
        'proof_trace':trace,
        'claim_eligible':eta>=40.0
    }

def verify_chain():
    if not LEDGER.exists():
        print('sandbox ledger absent: nothing to verify')
        return 0
    rows=[json.loads(x) for x in LEDGER.read_text().splitlines() if x.strip()]
    prev='genesis'
    ok=True
    for i,row in enumerate(rows,1):
        if row.get('previous_hash') != prev:
            print(f'CHAIN FAIL at entry {i}')
            ok=False
        core={k:v for k,v in row.items() if k!='hash'}
        expected=canonical_hash(core)
        if expected != row.get('hash'):
            print(f'HASH FAIL at entry {i}')
            ok=False
        print(f"{i} {row.get('previous_hash','')[:12]} -> {row.get('hash','')[:12]} eta={row.get('eta_score')} eligible={row.get('claim_eligible')}")
        prev=row.get('hash',prev)
    print('chain verification:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--task')
    ap.add_argument('--verify',action='store_true')
    ap.add_argument('--approve-write',action='store_true')
    args=ap.parse_args()

    if args.verify:
        return verify_chain()

    if not args.task:
        print('ERROR: --task is required unless --verify is used',file=sys.stderr)
        return 2

    if args.verify:
        return verify_chain()

    if not args.task:
        print('ERROR: --task is required unless --verify is used',file=sys.stderr)
        return 2

    task_path=Path(args.task).resolve()
    if not task_path.is_file():
        print('ERROR: task file not found',file=sys.stderr)
        return 2

    if SANDBOX not in task_path.parents and task_path.parent != SANDBOX:
        print('ERROR: task must be inside sandbox',file=sys.stderr)
        return 2

    task=json.loads(task_path.read_text())
    result=evaluate(task)
    root=merkle_root(result['proof_trace'])

    proposed={
        'timestamp':datetime.now(timezone.utc).isoformat(),
        'rules_version':RULES_VERSION,
        'task_sha256':sha256_file(task_path),
        'eta_score':result['eta_score'],
        'merkle_root':root,
        'claim_eligible':result['claim_eligible'],
        'proof_trace':result['proof_trace'],
        'write_approved':args.approve_write,
        'ledger_status':'sandbox_proposal_only'
    }
    proposed['hash']=canonical_hash(proposed)

    out=SANDBOX/'lattice_evaluator_result.json'
    out.write_text(json.dumps(proposed,indent=2,sort_keys=True)+'\n')

    ledger_status='sandbox_proposal_only'
    ledger_entry=None

    if args.approve_write:
        LEDGER.parent.mkdir(parents=True,exist_ok=True)
        resolved=LEDGER.resolve()
        if SANDBOX not in resolved.parents:
            print('ERROR: refusing ledger write outside sandbox',file=sys.stderr)
            return 3

        prev='genesis'
        if LEDGER.exists():
            lines=[x.strip() for x in LEDGER.read_text().splitlines() if x.strip()]
            if lines:
                prev=json.loads(lines[-1]).get('hash','genesis')

        ledger_entry={
            'timestamp':datetime.now(timezone.utc).isoformat(),
            'type':'sandbox_lattice_claim',
            'rules_version':RULES_VERSION,
            'task_sha256':proposed['task_sha256'],
            'eta_score':proposed['eta_score'],
            'merkle_root':proposed['merkle_root'],
            'claim_eligible':proposed['claim_eligible'],
            'previous_hash':prev
        }
        ledger_entry['hash']=canonical_hash(ledger_entry)

        with LEDGER.open('a',encoding='utf-8') as f:
            f.write(json.dumps(ledger_entry,sort_keys=True,separators=(',',':'))+'\n')

        ledger_status='sandbox_ledger_appended'

    proposed['ledger_status']=ledger_status
    if ledger_entry:
        proposed['ledger_entry_hash']=ledger_entry['hash']

    out.write_text(json.dumps(proposed,indent=2,sort_keys=True)+'\n')

    print(out)
    print(json.dumps(proposed,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
