#!/usr/bin/env python3
"""
Pod Workspace Consolidator
Finds all files and directories with 'pod' in their title/name across the tree
and safely relocates them into a unified workspace directory.
"""

import os
import shutil
from pathlib import Path

TARGET_WORKSPACE = Path("workspace/pods")

def consolidate_pods():
    TARGET_WORKSPACE.mkdir(parents=True, exist_ok=True)
    print(f"[*] Scanning repository for items containing 'pod' in their title...")
    
    moved_count = 0
    # Walk through workspace, avoiding the target workspace itself to prevent loops
    for root, dirs, files in os.walk(".", topdown=True):
        # Skip the destination workspace during traversal
        if "workspace" in Path(root).parts:
            continue
            
        all_items = files + dirs
        for item in all_items:
            if "pod" in item.lower():
                src_path = Path(root) / item
                
                # Avoid moving if it's already inside TARGET_WORKSPACE
                try:
                    src_path.relative_to(TARGET_WORKSPACE)
                    continue
                except ValueError:
                    pass
                
                dest_path = TARGET_WORKSPACE / item
                
                # Handle naming collisions
                if dest_path.exists():
                    base = dest_path.stem
                    ext = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = TARGET_WORKSPACE / f"{base}_{counter}{ext}"
                        counter += 1
                
                print(f"[+] Moving: {src_path} -> {dest_path}")
                try:
                    shutil.move(str(src_path), str(dest_path))
                    moved_count += 1
                except Exception as e:
                    print(f"[!] Error moving {src_path}: {e}")

    print(f"[✔] Successfully consolidated {moved_count} pod-related items into {TARGET_WORKSPACE}/")

if __name__ == "__main__":
    consolidate_pods()
