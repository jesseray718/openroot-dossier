#!/usr/bin/env python3
"""
Agape Combinatory Spirdering & Pathway Compiler (R=1, c=0)
Crawls home/Termux directories, extracts modular Turing tidbits,
compounds pathways, and logs COMPOST analytics in real time.
"""
import os
import json
import time
import hashlib

def crawl_termux_and_home():
    print("[SPIRDER] Crawling local filesystem for Turing tidbits and receipts...")
    tidbits = []
    search_roots = [
        os.path.expanduser("~/openroot"),
        os.path.expanduser("~/.termux"),
        os.path.expanduser("~/storage/downloads")
    ]
    
    for base in search_roots:
        if os.path.exists(base):
            for root, _, files in os.walk(base):
                if '.git' in root or '__pycache__' in root:
                    continue
                for f in files:
                    if f.endswith(('.py', '.sh', '.json', '.jsonl', '.md', '.txt')):
                        full_path = os.path.join(root, f)
                        try:
                            size = os.path.getsize(full_path)
                            tidbits.append({"path": full_path, "size": size})
                        except Exception:
                            pass
    return tidbits[:50] # High-density cap

def compile_combinatory_pods(tidbits):
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    pod_id = f"combinatory_pod_{timestamp}"
    
    hashes = []
    for t in tidbits:
        h = hashlib.sha256(t["path"].encode()).hexdigest()[:12]
        hashes.append(h)
    
    # Calculate combinatory synergy index (Merkle-like fold)
    combined_hash = hashlib.sha256("".join(hashes).encode()).hexdigest() if hashes else "0"
    
    pod_payload = {
        "pod_id": pod_id,
        "timestamp": timestamp,
        "alignment_metrics": {"R": 1.0, "coordination_cost": 0.0},
        "tidbits_indexed": len(tidbits),
        "combinatory_synergy_hash": combined_hash,
        "manifest": tidbits
    }
    
    out_path = f"workareas/agape_pods/{pod_id}.json"
    with open(out_path, "w") as f:
        json.dump(pod_payload, f, indent=2)
        
    # Real-time COMPOST analytics extraction log
    compost_log = f"workareas/compost_logs/compost_{timestamp}.log"
    with open(compost_log, "w") as cl:
        cl.write(f"COMPOST Analytics Extraction Report [{timestamp}]\n")
        cl.write(f"Indexed Tidbits: {len(tidbits)}\n")
        cl.write(f"Synergy Hash: {combined_hash}\n")
        cl.write("Friction extracted, converted into negentropic pathway asset.\n")
        
    print(f"[SPIRDER] Compiled combinatory pod -> {out_path}")
    print(f"[COMPOST] Analytics extracted -> {compost_log}")
    return out_path

if __name__ == "__main__":
    tidbits = crawl_termux_and_home()
    compile_combinatory_pods(tidbits)
