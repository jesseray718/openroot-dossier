#!/usr/bin/env bash
set -uo pipefail
PKG="com.inspiredandroid.kai"
CORE_IP="${CORE_IP:-100.122.169.43}"
PROBE_PORTS="${PROBE_PORTS:-9999,11434,8080,3000,8765}"
REPO="https://github.com/SimonSchubert/Kai"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="${HOME}/openroot"
OUT="${ROOT}/workareas/kai_forensics"
RUN="\( {OUT}/run_ \){TS}"
SRCDIR="${OUT}/src"
mkdir -p "${RUN}" || { echo "FATAL: cannot create ${RUN}" >&2; exit 1; }
echo "[*] Output: ${RUN}"
step() { printf '\n===[ %s ]===\n' "$1"; }
note() { printf '    %s\n' "$1"; }

step "1. Device recon: locate Kai package"
if command -v pm >/dev/null 2>&1; then
  pm path "\( {PKG}" 2>/dev/null | tee " \){RUN}/pm_path.txt" && note "APK path(s) captured."
else
  note "pm not callable (normal in Termux). Recorded."
  echo "pm-unavailable: use adb shell pm path \( {PKG} after wireless pairing." > " \){RUN}/pm_path.txt"
fi
for d in "\( {HOME}/storage/downloads" " \){HOME}/storage/shared/Android/data/\( {PKG}" " \){HOME}/storage/shared/Documents"; do
  if [ -d "${d}" ]; then
    note "Scanning ${d}"
    find "\( {d}" -maxdepth 3 \( -iname '*kai*' -o -iname '*.kai*' \) 2>/dev/null | head -50 >> " \){RUN}/shared_storage_hits.txt" || true
  fi
done
if [ -s "${RUN}/shared_storage_hits.txt" ]; then
  note "\( (wc -l < " \){RUN}/shared_storage_hits.txt") Kai-named files in shared storage."
else
  note "No Kai-named files in shared storage (private app data expected)."
fi

step "2. Live process & socket snapshot"
{ ps -A 2>/dev/null || ps 2>/dev/null; } > "${RUN}/processes_all.txt"
grep -i -E 'kai|inspiredandroid' "\( {RUN}/processes_all.txt" > " \){RUN}/processes_kai.txt" || true
if [ -s "${RUN}/processes_kai.txt" ]; then
  cat "${RUN}/processes_kai.txt"
else
  note "No Kai processes visible from this shell (sandbox expected)."
fi
{ ss -tulpn 2>/dev/null || cat /proc/net/tcp /proc/net/tcp6 2>/dev/null; } > "${RUN}/sockets_snapshot.txt" || true
note "Socket table captured (\( (wc -l < " \){RUN}/sockets_snapshot.txt" 2>/dev/null || echo 0) lines)."

step "3. Relay endpoint probe (9999 is empirical only)"
if command -v python3 >/dev/null 2>&1; then
  python3 "\( {OUT}/kai_relay_probe.py" " \){CORE_IP}" "\( {PROBE_PORTS}" | tee " \){RUN}/relay_probe.txt"
  note "Probe done. open on 9999 would identify a local relay; closed = nothing listening."
else
  note "python3 missing — skip probe."
fi

step "4. Acquire upstream source (cached) & map real code paths"
if [ ! -d "${SRCDIR}/.git" ]; then
  note "Cloning ${REPO} (shallow)..."
  git clone --depth 1 "\( {REPO}" " \){SRCDIR}" > "${RUN}/clone.log" 2>&1 && note "Cloned OK." || { note "Clone FAILED (see clone.log)"; SRCDIR=""; }
else
  note "Using cached clone at ${SRCDIR}"
  git -C "\( {SRCDIR}" log -1 --format='HEAD: %h %ci %s' 2>/dev/null | tee " \){RUN}/source_revision.txt" || true
fi
KT_COUNT=0
SRC_MAP="${RUN}/source_map.txt"
: > "${SRC_MAP}"
if [ -n "\( {SRCDIR}" ] && [ -d " \){SRCDIR}" ]; then
  KT_COUNT=\( (find " \){SRCDIR}" -name '*.kt' 2>/dev/null | wc -l)
  note "${KT_COUNT} Kotlin files."
  mapgrep() {
    printf '\n== %s ==\n' "$1" >> "${SRC_MAP}"
    grep -rilE --include='*.kt' "$2" "\( {SRCDIR}" 2>/dev/null | sed "s| \){SRCDIR}/||" | head -12 >> "${SRC_MAP}" || true
  }
  mapgrep "Heartbeat / autonomous scheduling" 'heartbeat|WorkManager|AlarmManager'
  mapgrep "Persistent memory layer" 'memory|remember|RoomDatabase|DataStore|sqlite'
  mapgrep "Provider fallback cascade" 'fallback|OpenAI-compatible|provider'
  mapgrep "Tool execution & shell sandbox" 'ProcessBuilder|execute_shell|proot|sandbox|Runtime\.getRuntime'
  mapgrep "Networking / possible relay listener" 'ServerSocket|port|9999|localhost|MCP'
  note "Source map written."
  grep -A4 '^==' "${SRC_MAP}" 2>/dev/null | head -40 || true
fi

step "5. Deep-dive doc"
if command -v python3 >/dev/null 2>&1 && [ -n "\( {SRCDIR}" ] && [ -d " \){SRCDIR}" ]; then
  python3 - "\( {SRCDIR}" " \){RUN}" "${KT_COUNT}" << 'PYDOC'
import json, pathlib, re, sys, time
src, run, kt_count = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
now = time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
TOPICS = [
  ("Heartbeat (autonomous cycles)", ["heartbeat", "WorkManager", "AlarmManager", "schedule"],
   "OpenRoot analog: a15 hybrid daemon / mesh sync loops."),
  ("Persistent memory", ["memory", "remember", "Room", "DataStore", "sqlite"],
   "OpenRoot analog: reply_cache.jsonl + FTS5 openroot pods + ledger."),
  ("Provider fallback chain", ["fallback", "provider", "OpenAI-compatible", "LiteRT"],
   "OpenRoot analog: local Ollama cascade (this router refuses cloud by default)."),
  ("Tool execution / shell sandbox", ["ProcessBuilder", "execute_shell", "proot", "sandbox", "Runtime.getRuntime"],
   "AUDIT TARGET: scope and guards of any AI-driven shell on device."),
  ("Relay / listener surface", ["ServerSocket", "9999", "localhost", "MCP"],
   "Resolves channel-9999: does Kai itself ever listen? Empirical probe answers this."),
]
lines = [f"# Kai 9000 Deep Dive — {now}", "",
         f"Source: github.com/SimonSchubert/Kai @ {src.resolve()}",
         f"Kotlin files scanned: {kt_count}", ""]
index = {}
for title, keys, note in TOPICS:
    lines += [f"## {title}", f"*{note}*", ""]
    hits = {}
    for f in src.rglob("*.kt"):
        try: text = f.read_text(errors="replace")
        except OSError: continue
        found = {k for k in keys if re.search(re.escape(k), text, re.I)}
        if found: hits[str(f.relative_to(src))] = sorted(found)
    for path, ks in sorted(hits.items())[:12]:
        lines.append(f"- `{path}` — {', '.join(ks)}")
    lines.append("")
    index[title] = len(hits)
doc = run / f"DEEPDIVE_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.md"
doc.write_text("\n".join(lines))
(run / "deepdive_index.json").write_text(json.dumps({"generated": now, "latest": str(doc), "topics": index}, indent=2))
print(f"[ok] deep-dive doc -> {doc}")
print(f"[ok] topic hit counts: {json.dumps(index)}")
PYDOC
else
  note "Skipping doc generation (needs python3 + cloned source)."
fi

step "6. Sealing receipt"
if command -v python3 >/dev/null 2>&1; then
  RECEIPT=\( (python3 - " \){RUN}" << 'PYREC'
import hashlib, json, pathlib, sys, time
run = pathlib.Path(sys.argv[1])
files = {}
for p in sorted(run.rglob("*")):
    if p.is_file():
        files[str(p.relative_to(run))] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
print(json.dumps({
  "schema": "kai_fx_run_v1",
  "target_package": "com.inspiredandroid.kai",
  "generated_utc": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
  "artifact_count": len(files),
  "artifacts_sha256_16": files,
}, indent=2))
PYREC
)
  echo "\( {RECEIPT}" | tee " \){RUN}/receipt.json"
  ART_N=\( (echo " \){RECEIPT}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["artifact_count"])' 2>/dev/null || echo 0)
  note "Sealed ${ART_N} artifacts with checksums."
else
  find "\( {RUN}" -type f > " \){RUN}/receipt_filelist.txt"
  note "python3 absent — plain file list as receipt."
fi

printf '\n==============================================\n INVESTIGATION COMPLETE\n==============================================\n'
echo " All artifacts : ${RUN}"
echo " Relay probe   : ${RUN}/relay_probe.txt"
echo " Source map    : ${RUN}/source_map.txt"
echo " Deep-dive doc : ${RUN}/DEEPDIVE_*.md"
echo ""
echo " NEXT"
echo " 1. If 9999 OPEN, cross-check Kai provider/MCP settings on phone."
echo " 2. Private data (root-free): pair wireless ADB then:"
echo "      adb shell pm path ${PKG}"
echo "      adb shell dumpsys package ${PKG} | head -80"
echo "      adb backup -f kai.ab ${PKG}"
echo " 3. Re-run: bash ${OUT}/kai9000_investigator.sh"
exit 0
