import os, sys, py_compile, argparse

ROOT_DIR = "/home/jesse/openroot"
THEME_FILE = "/home/jesse/openroot/coder/THEME.md"

def scan_and_compile():
    print(f"=== OPENROOT CODER STACK (DRY AUDIT) ===")
    red_files = []
    missing_files = []
    green_count = 0
    
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ROOT_DIR)
                
                # Guard against broken symlinks or missing files during scan
                if not os.path.isfile(full_path):
                    missing_files.append(rel_path)
                    continue

                try:
                    py_compile.compile(full_path, doraise=True)
                    green_count += 1
                except py_compile.PyCompileError as err:
                    red_files.append((rel_path, str(err.msg)))
                except Exception as err:
                    red_files.append((rel_path, f"IO Error: {err}"))

    print(f"Compile Audit: {green_count} GREEN | {len(red_files)} RED | {len(missing_files)} DANGLING/MISSING")
    
    with open(THEME_FILE, "w") as f:
        f.write("# OPENROOT HEALTH & THEME LOG\n\n")
        f.write(f"- **GREEN PyCompile Count:** {green_count}\n")
        f.write(f"- **RED PyCompile Count:** {len(red_files)}\n")
        f.write(f"- **Dangling/Missing Symlinks:** {len(missing_files)}\n\n")
        
        if red_files:
            f.write("## Syntax Errors (RED)\n")
            for rpath, msg in red_files:
                f.write(f"- `{rpath}`: {msg}\n")
            f.write("\n")
            
        if missing_files:
            f.write("## Missing / Broken Symlinks\n")
            for mpath in missing_files:
                f.write(f"- `{mpath}`\n")
                
    print(f"Updated {THEME_FILE}")
    return len(red_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dry-run Openroot Coder Loop")
    parser.add_argument("--review", action="store_true", help="Run model review (dry)")
    args = parser.parse_args()

    red_count = scan_and_compile()
    
    if args.review:
        print("\n[REVIEW MODE] Ollama/Qwen model review hook triggered (Dry-run mode, no git mutations).")
