#!/usr/bin/env python3
"""Two-step, human-gated promotion tool for sandbox lattice claims.

Stage mode copies an eligible sandbox entry into a staging ledger.
Seal mode requires an explicit staging entry hash and creates a canonical
claim in a separate staging-side canonical ledger.

This tool never modifies the live OpenRoot tree.
"""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

SANDBOX=Path(__file__).resolve().parent
LIVE_ROOT=Path('/home/jesse/openroot').resolve()
SANDBOX_LEDGER=SANDBOX/'acre/ledger.jsonl'
STAGING_LEDGER=SANDBOX/'promotion/staging_ledger.jsonl'
CANONICAL_LEDGER=SANDBOX/'promotion/canonical_ledger.jsonl'

def canonical_hash(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
    ).hexdigest()

def load_entries(path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def verify_sandbox_chain():
    rows=load_entries(SANDBOX_LEDGER)
    prev='genesis'
    for i,row in enumerate(rows,1):
        if row.get('previous_hash') != prev:
            return False,f'chain failure at entry {i}'
        core={k:v for k,v in row.items() if k!='hash'}
        if canonical_hash(core) != row.get('hash'):
            return False,f'hash failure at entry {i}'
        prev=row.get('hash',prev)
    return True,f'verified {len(rows)} entries'

def append_entry(path,entry):
    path.parent.mkdir(parents=True,exist_ok=True)
    rows=load_entries(path)
    previous=rows[-1]['hash'] if rows else 'genesis'
    entry['previous_hash']=previous
    entry['hash']=canonical_hash(entry)
    with path.open('a',encoding='utf-8') as f:
        f.write(json.dumps(entry,sort_keys=True,separators=(',',':'))+'\n')
    return entry

def stage(args):
    ok,message=verify_sandbox_chain()
    if not ok:
        print('ERROR:',message,file=sys.stderr); return 2

    matches=[x for x in load_entries(SANDBOX_LEDGER)
             if x.get('hash','').startswith(args.sandbox_entry_hash)]
    if len(matches)!=1:
        print('ERROR: sandbox entry hash must match exactly one entry',file=sys.stderr)
        return 2

    source=matches[0]
    if not source.get('claim_eligible',False):
        print('ERROR: sandbox entry is not claim-eligible',file=sys.stderr)
        return 3

    staged={
        'timestamp':datetime.now(timezone.utc).isoformat(),
        'type':'canonical_staging_pending',
        'sandbox_entry_hash':source['hash'],
        'task_sha256':source.get('task_sha256'),
        'rules_version':source.get('rules_version'),
        'eta_score':source.get('eta_score'),
        'merkle_root':source.get('merkle_root'),
        'claim_eligible':source.get('claim_eligible'),
        'approval_status':'pending_human_review'
    }
    staged['hash']=canonical_hash(staged)
    entry=append_entry(STAGING_LEDGER,staged)

    receipt={
        'timestamp':datetime.now(timezone.utc).isoformat(),
        'operation':'stage',
        'sandbox_entry_hash':source['hash'],
        'staging_entry_hash':entry['hash'],
        'staging_ledger':str(STAGING_LEDGER),
        'canonical_status':'not_canonical'
    }
    receipt['hash']=canonical_hash(receipt)
    out=SANDBOX/'promotion/stage_receipt.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(out)
    print(json.dumps(receipt,indent=2))
    return 0

def seal(args):
    rows=load_entries(STAGING_LEDGER)
    matches=[x for x in rows if x.get('hash','').startswith(args.staging_entry_hash)]
    if len(matches)!=1:
        print('ERROR: staging entry hash must match exactly one entry',file=sys.stderr)
        return 2

    staged=matches[0]
    if staged.get('approval_status') != 'pending_human_review':
        print('ERROR: staging entry is not pending human review',file=sys.stderr)
        return 3

    canonical={
        'timestamp':datetime.now(timezone.utc).isoformat(),
        'type':'canonical_claim_sealed',
        'staging_entry_hash':staged['hash'],
        'sandbox_entry_hash':staged.get('sandbox_entry_hash'),
        'task_sha256':staged.get('task_sha256'),
        'rules_version':staged.get('rules_version'),
        'eta_score':staged.get('eta_score'),
        'merkle_root':staged.get('merkle_root'),
        'claim_eligible':staged.get('claim_eligible'),
        'approver':args.approver,
        'canonical_status':'sandbox_canonical_only'
    }
    canonical['hash']=canonical_hash(canonical)
    entry=append_entry(CANONICAL_LEDGER,canonical)

    receipt={
        'timestamp':datetime.now(timezone.utc).isoformat(),
        'operation':'seal',
        'staging_entry_hash':staged['hash'],
        'canonical_entry_hash':entry['hash'],
        'approver':args.approver,
        'canonical_ledger':str(CANONICAL_LEDGER),
        'live_tree_modified':False
    }
    receipt['hash']=canonical_hash(receipt)
    out=SANDBOX/'promotion/seal_receipt.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(out)
    print(json.dumps(receipt,indent=2))
    return 0

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='command',required=True)

    stage_parser=sub.add_parser('stage')
    stage_parser.add_argument('--sandbox-entry-hash',required=True)

    seal_parser=sub.add_parser('seal')
    seal_parser.add_argument('--staging-entry-hash',required=True)
    seal_parser.add_argument('--approver',required=True)

    args=ap.parse_args()
    if args.command=='stage':
        return stage(args)
    return seal(args)

if __name__=='__main__':
    raise SystemExit(main())
