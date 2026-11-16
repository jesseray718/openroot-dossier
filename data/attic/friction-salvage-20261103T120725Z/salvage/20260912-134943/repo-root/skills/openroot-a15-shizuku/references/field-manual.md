# OpenRoot Field Manual: Verified Facts for a stdlib-only Termux + Shizuku Workflow on Galaxy A15 (Android 14/15)

## TL;DR
- **The stack is viable and well-supported**: Shizuku gives you a UID 2000 (ADB `shell`) shell on-device via `rish`, invoked non-interactively as `rish -c 'cmd'`; this unlocks `pm grant`, `cmd appops`, `cmd deviceidle`, `settings put`, and — critically for your energy/thermal logging — reliable reads of battery `current_now`/`voltage_now` (AOSP grants the `shell` domain explicit `sysfs_batteryinfo` read). The single hard limitation to design around: **Shizuku must be manually restarted after every reboot** on a non-rooted device, with no fully-automated no-PC workaround.
- **Background persistence** is a layered problem on Samsung One UI: combine `termux-wake-lock`, `dumpsys deviceidle whitelist +com.termux`, `cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow`, and manual One UI "Never sleeping apps" / excluded-apps entries. No single command fully defeats Samsung's aggressive killing.
- **Voice input**: `termux-speech-to-text` (Termux:API) uses the Android/Google recognizer and streams text to stdout — the lowest-friction path with ~0 extra persistent RAM. Offline whisper.cpp tiny (~390 MB RAM) or Vosk small (~300 MB RAM) are feasible on the A15's Helio G99 but compete with llama-server for the 4 GB base RAM. None of the recommended commands trip Samsung Knox.

## Key Findings
1. **rish is the core primitive.** `rish -c 'command'` runs one command at ADB shell privilege (UID 2000) and exits; `echo 'cmd' | rish` (stdin pipe) also works. It passes arguments straight to a remote `/system/bin/sh -c`. Confirmed against the official Shizuku-API README.
2. **Shizuku does not survive reboot without root.** Wireless-debugging pairing persists, but the *service* must be restarted from the Shizuku app after each boot. This is the central operational constraint.
3. **Shell UID reliably reads battery telemetry** (`sysfs_batteryinfo` is explicitly granted to the `shell` SELinux domain in AOSP base policy), enabling direct P = V·I energy measurement. Thermal zones and CPU frequency are usually readable at shell UID but are NOT provably granted in AOSP base policy — test on-device and fall back to `dumpsys thermalservice`.
4. **Samsung/MediaTek battery current sign and scaling must be measured empirically** — do not assume the Linux canonical "negative = discharging."
5. **Knox is safe.** ADB/Shizuku usage does not trip the Knox e-fuse; only bootloader unlock or root does.

**Hardware baseline (anchor your budgets to this):** The Galaxy A15 4G base model ships with **4 GB LPDDR4X RAM** (6 GB / 8 GB variants exist), **MediaTek Helio G99 (6 nm): octa-core 2×2.2 GHz Cortex-A76 + 6×2.0 GHz Cortex-A55, Mali-G57 MC2**, 128 GB UFS 2.2, 5000 mAh battery, launched on Android 14 / One UI 6 (upgradable to One UI 7), per GSMArena's Galaxy A15 4G review. Your "~3.5 GB one-hot" working budget is the practical residual of the 4 GB base configuration.

## Details

### 1. SHIZUKU + RISH SETUP

**1.1 Wireless-debugging pairing (no PC, Android 14/15).** The on-device wireless-debugging start method still works on Android 14/15 and is the standard no-PC path. Procedure:
1. Settings → About phone → Software information → tap **Build number** 7× to enable Developer options.
2. Developer options → enable **Wireless debugging** (device must be on Wi-Fi).
3. Open Shizuku → "Start via Wireless debugging" → tap **Pairing**. Grant Shizuku the notification permission (needed so the pairing notification appears).
4. In parallel, go to Developer options → Wireless debugging → **Pair device with pairing code**. Enter the 6-digit code into Shizuku's pairing prompt.
5. Back in Shizuku, under "Start via Wireless debugging," tap **Start**. Shizuku opens a transient screen and reports "Shizuku is running … adb."

One UI quirk: if Shizuku is stuck "Searching for wireless debugging service," toggle Wireless debugging off/on from the Developer options popup. Wireless debugging auto-disables after Shizuku starts — this is expected; the service persists until reboot.

**1.2 Installing rish into Termux.** In Shizuku → **"Use Shizuku in terminal apps"** → export the two files (`rish` and `rish_shizuku.dex`). Then in Termux (after `termux-setup-storage`):
```
mv ~/storage/shared/rish/rish /data/data/com.termux/files/usr/bin/rish
mv ~/storage/shared/rish/rish_shizuku.dex /data/data/com.termux/files/usr/bin/rish_shizuku.dex
chmod +x /data/data/com.termux/files/usr/bin/rish
```
The `rish` script needs `RISH_APPLICATION_ID` set to the terminal's package. The current script auto-defaults to `com.termux` if unset: `[ -z "$RISH_APPLICATION_ID" ] && export RISH_APPLICATION_ID="com.termux"`. You can also export it explicitly in `~/.bashrc`.

**Android 14+ dex constraint (critical):** On SDK ≥ 34, `app_process` refuses to load a *writable* dex. The current rish script handles this by `chmod 400 rish_shizuku.dex`; if the dex sits somewhere it can't have its write bit removed, you must copy it into the app's private dir (`/data/data/com.termux/...`). The internal invocation is:
```
/system/bin/app_process -Djava.class.path="$DEX" /system/bin --nice-name=rish rikka.shizuku.shell.ShizukuShellLoader "$@"
```

**1.3 Non-interactive / scripted use.** Four modes, per the awesome-shizuku reference:
- `rish` → interactive `/system/bin/sh` at UID 2000
- `rish exec /path/to/shell` → interactive custom shell
- `rish -c 'command'` → single command then exit (**this is your scripting primitive**)
- `echo 'command' | rish` → read one command from stdin

Notes for scripting:
- `RISH_PRESERVE_ENV`: `0` = keep remote env; `1` = replace remote env with local's. Under an ADB backend it defaults to `0`. Because Termux sets `PATH`/`LD_PRELOAD` to its private paths — which the ADB shell user cannot access — leaving `RISH_PRESERVE_ENV=0` avoids `cd`/path breakage in the remote shell.
- Quoting: arguments pass straight through to `/system/bin/sh -c '…'`, so quote exactly as you would for `sh -c`. From Python, prefer `subprocess.run(["rish","-c",cmd], …)` to avoid a second shell layer.
- Exit codes / stdout / stderr propagate normally from the remote command through rish.

**1.4 Reboot behavior.** Confirmed: on a non-rooted device Shizuku must be started via ADB/wireless debugging **each time after reboot**; only the pairing persists. There is no supported fully-automated no-PC restart. Community-reported approaches (all with caveats — flag as unverified for the A15):
- Scripts that re-run the wireless-debugging connect flow (e.g. the "Automatically activate Shizuku in Android 14+" GitHub discussion #462) require reading the current wireless-debugging port and can hit "more than one device/emulator" when multiple paired endpoints exist (fix: `adb disconnect` then `adb connect localhost:PORT`).
- The practical OpenRoot answer: keep reboots rare, and script a single post-reboot "bring-up" task (see §3).

**1.5 aShell / aShell You.** `aShell` (sunilpaulmathew, GPLv3, on F-Droid/IzzyOnDroid; requires `moe.shizuku.manager.permission.API_V23`) is a GUI ADB shell that integrates Shizuku *directly via the Shizuku-API AIDL* (it does NOT use rish). Features: bundled command examples, handles continuous commands (logcat/top), search within output, **save last output to a text file, and bookmark frequently-used commands**. `aShell You` (a separate Material-You rewrite, ashellyou.github.io) adds sending commands to other devices over OTG/Wireless Debugging and a push/pull file manager. When to prefer over rish: interactive exploration, saved/bookmarked command sets, and one-off privileged commands from a GUI. For *scripted, headless, Python-driven* use, **rish is correct** because aShell has no CLI entry point. Other frontends: ShizuShell. `rish` remains the only option for arbitrary terminal/script runners.

**1.6 Common rish failure modes.**
- **"Shizuku is not running"** — service not started after reboot (see 1.4). Restart via Shizuku app.
- **RISH_APPLICATION_ID not set** — first test command prints an error; set the env var or use the auto-defaulting script.
- **"On Android 14+, app_process cannot load writable dex"** — remove write bit (`chmod 400 rish_shizuku.dex`) or move dex into app-private dir.
- **"Cannot find …/rish_shizuku.dex"** — dex not beside the rish binary / wrong path.
- **`cd`/PATH failures inside remote shell** — RISH_PRESERVE_ENV / Termux path issue; leave preserve-env at 0.

### 2. WHAT SHELL UID (2000) UNLOCKS ON ANDROID 14/15

**2.1 `pm grant <pkg> <permission>`** — grants `signature`/`development`/`appop`-backed permissions the app declares in its manifest. Confirmed grantable to a manifest-declaring app: `android.permission.WRITE_SECURE_SETTINGS`, `PACKAGE_USAGE_STATS`, `READ_LOGS`, `DUMP`, `POST_NOTIFICATIONS`, etc. Example (Termux:API declares these):
```
rish -c 'pm grant com.termux.api android.permission.WRITE_SECURE_SETTINGS'
rish -c 'pm grant com.termux.api android.permission.READ_LOGS'
```
Limitations: the permission must be declared in the target app's manifest and be of a grantable protection level; `pm grant` for non-runtime/non-grantable perms fails. On some OEM builds UID 2000 has historically lacked `GRANT_RUNTIME_PERMISSIONS` for arbitrary runtime perms (seen as `SecurityException: … neither user 2000 nor current process has android.permission.GRANT_RUNTIME_PERMISSIONS`), but standard `WRITE_SECURE_SETTINGS`/`READ_LOGS`/`DUMP` grants work on stock Samsung.

**2.2 `cmd appops` / `appops set`** — controls background execution app-ops:
```
rish -c 'cmd appops set com.termux RUN_IN_BACKGROUND allow'
rish -c 'cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow'
```
`appops` is a shortcut for `cmd appops`. Caveat (XDA-reported): appops does not stop/allow every app reliably (some use JobScheduler/sync paths that bypass it), so treat it as necessary-but-not-sufficient. Verify with `cmd appops get com.termux`.

**2.3 `settings put global/secure/system`** — requires WRITE_SECURE_SETTINGS (which UID 2000 has inherently). Relevant keys for keeping processes alive exist, but many are GMS-overwritten. Note the documented gotcha (tweakradje): `device_config` changes are restored by GMS ~5 minutes after boot. Be conservative (see §6 for danger keys).

**2.4 `cmd deviceidle` / `dumpsys deviceidle whitelist`** — Doze battery-optimization exemption:
```
rish -c 'dumpsys deviceidle whitelist +com.termux'
rish -c 'dumpsys deviceidle whitelist +com.termux.api'
```
Remove with `-com.termux`. Persistence: user-whitelist entries persist across reboot on Android 10+ (XDA-reported; user vs system sections differ). `cmd deviceidle` also supports `force-idle`, `step`, `disable`, `enable` for testing Doze. `dumpsys deviceidle sys-whitelist` lists system apps.

**2.5 Samsung "Sleeping apps / Deep sleeping apps."** Samsung's App power monitor is separate from AOSP Doze. Per **Samsung's official developer documentation (developer.samsung.com/mobile/app-management.html)**: "Background applications that have not been used for about **3 days** … will go into the sleeping mode" (a bucket restriction limiting Job, Alarm, and Foreground-service), and deep sleeping applies to apps "not been used for a long period of time (currently set to **16 days**, but subject to change according to Samsung policies)" (only active when the user opens them). Exceptions are set at **Settings → Battery and device care → Battery → Background usage limits → Never sleeping apps**. **There is no reliable documented shell command to add an app to Samsung's "Never sleeping apps" list** — it is a Samsung-proprietary list, not the AOSP deviceidle whitelist. Treat this as a manual GUI step. Also toggle off "Put unused apps to sleep," and add Termux to Device care → Memory → Excluded apps.

**2.6 System/telemetry commands at shell UID.** `cmd package`/`pm`, `am start`/`am broadcast`, `input`, `screencap`, `screenrecord`, `dumpsys battery`, `cmd thermalservice`/`dumpsys thermalservice`, `cmd stats` all run at shell UID. `dumpsys battery` gives level/temperature/voltage; `dumpsys thermalservice` prints a "Current temperatures from HAL" section with `Temperature{mValue=…, mType=…, mName=…}` where mValue is °C (float) and mType is the Android enum (CPU=0, GPU=1, BATTERY=2, SKIN=3, USB_PORT=4, POWER_AMPLIFIER=5, …). Caveat: on some devices the HAL temperature list is empty even when connected — confirm on the A15.

**2.7 Thermal / CPU telemetry (Helio G99).**
- **untrusted_app (normal Termux app UID) is BLOCKED** from `/sys/class/thermal` (labeled `sysfs_thermal`); documented AVC denial: `avc: denied { search } … tcontext=u:object_r:sysfs_thermal:s0 tclass=dir permissive=0`.
- **shell UID via rish** can *usually* read `/sys/class/thermal/thermal_zone*/temp` (millidegree C, per kernel.org sysfs-class-thermal ABI) and `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq` (kHz, per kernel.org cpufreq docs), but AOSP base `shell.te` does NOT contain a provable `allow shell sysfs_thermal` / `sysfs_devices_system_cpu` read line — access relies on world-readable DAC + vendor policy. **Test empirically**: `rish -c 'cat /sys/class/thermal/thermal_zone0/temp'`; if denied, use `dumpsys thermalservice`.
- `scaling_cur_freq` is the governor's *requested* freq; `cpuinfo_cur_freq` is the HW-read actual (often root-only).

**2.8 Battery / power measurement (your joules-per-task goal).**
- **`shell` is explicitly granted `sysfs_batteryinfo` read in AOSP base `shell.te`** (`allow shell sysfs_batteryinfo:file r_file_perms;`). Via rish you can reliably read `/sys/class/power_supply/battery/{current_now,voltage_now,charge_counter}`.
- **Units (Linux power_supply ABI, kernel.org):** `voltage_now` in µV, `current_now` in µA, `charge_counter` in µAh. Instantaneous power P = V·I (watts after µ→base conversion); integrate over the task for joules.
- **Sign/scaling on Samsung/MediaTek: MEASURE, don't assume.** The Linux canonical is negative = discharging (Sebastian Reichel's ABI commit), but the kernel itself documents *three* inconsistent driver conventions; Samsung/MediaTek gauges may invert the sign or report mA rather than µA. Validate against `POWER_SUPPLY_STATUS` (Charging/Discharging — unambiguous) and a known load before trusting the sign. (The A15's Helio G99 platform likely uses a MediaTek PMIC fuel gauge, not a Samsung-proprietary one — another reason to calibrate.)
- **Most accurate non-root method:** high-frequency sampling of `voltage_now × current_now` from sysfs via rish (direct fuel-gauge reads), with trapezoidal integration for energy. `dumpsys batterystats` (Battery Historian input) gives only *modeled* per-UID mAh estimates from the PowerProfile, not direct measurement — use it as a cross-check, not ground truth. `charge_counter` deltas (µAh × nominal voltage) give a coarser but drift-free energy estimate over longer windows.

**2.9 What shell UID CANNOT do (it is NOT root).** Cannot write to other apps' `/data`; cannot remount/modify system partitions; cannot set CPU governors or write most `/sys` thermal/cpufreq nodes (write is neverallow'd even where read works); cannot read `/sys/fs/selinux/policy`; cannot `setenforce`. `rish` under ADB backend is UID 2000 / `u:r:shell:s0`, confirmed by `whoami`.

### 3. TERMUX INTEGRATION & BACKGROUND PERSISTENCE

**3.1 `termux-wake-lock` / `termux-wake-unlock`.** `termux-wake-lock` acquires a partial wake lock (CPU stays awake, prevents deep sleep); `termux-wake-unlock` releases it. First invocation may show a consent popup once. State is exposed via the persistent Termux notification (id 1337; `termux-notification-list | jq …` can detect "wake lock held"). Call `termux-wake-lock` as the first line of any long-running/boot script.

**3.2 Termux:API commands (install `pkg install termux-api` + the Termux:API app from the same source/F-Droid).**
- `termux-battery-status` → JSON: `{"health","percentage","plugged","status","temperature","current"}` (current in µA on most devices; sign per device). Good sanity cross-check for §2.8.
- `termux-speech-to-text` → converts speech to text, streaming partial matches to stdout (see §4).
- `termux-tts-speak [-e engine] [-l lang] [-p pitch] [-r rate] [-s stream] "text"` → speaks via system TTS (streams: ALARM, MUSIC, NOTIFICATION, RING, SYSTEM, VOICE_CALL).
- `termux-notification` → supports `--title`, `--content`, `--sound`, `--vibrate`, action buttons (`--button1`/`--button1-action`), and ongoing notifications (`--ongoing`); `termux-notification-remove <id>`.
- `termux-toast` → transient popup; `termux-dialog` → interactive dialogs (multiple input types); `termux-clipboard-get`/`termux-clipboard-set`; `termux-sensor` → sensor stream JSON; `termux-vibrate`, `termux-volume`, `termux-location`, `termux-job-scheduler`.
- All emit JSON to stdout (parse with Python `json`); must be called from Termux's native env, not inside proot.

**3.3 Termux:Widget & `~/.shortcuts`.** Install Termux:Widget (F-Droid, com.termux.widget) and start Termux once so bootstrap files exist. Requirements (from the official README):
```
mkdir -p ~/.shortcuts && chmod -R 700 ~/.shortcuts
mkdir -p ~/.shortcuts/tasks   # background (non-terminal) scripts
mkdir -p ~/.shortcuts/icons
```
Termux home (`/data/data/com.termux/files/home`) and prefix must be 0700. Scripts must be executable. Add the resizable widget to the home screen; tap a script to run it (foreground scripts open a terminal session). **Android ≥ 10 restriction:** background activity-start limits mean terminal-session scripts may not surface until you tap the Termux notification. Press the widget's refresh button after adding/renaming scripts.

**3.4 Other add-ons.** Termux:Boot, Termux:Float, Termux:Styling, Termux:Task (for Tasker), Termux:API, Termux:Widget all remain available on F-Droid. Termux:Tasker (via the Termux:Task add-on) and Termux:Float both still exist.

**3.5 `termux-boot`.** Install Termux:Boot (com.termux.boot, F-Droid), then **launch the app once** so it's allowed to run at boot. Put scripts in `~/.termux/boot/`; multiple files run in sorted order. Example: a file `~/.termux/boot/start` containing `termux-wake-lock && sshd`. Limitations: on Android 10+ / Samsung, boot execution is fragile — Samsung's aggressive battery management and background-start restrictions frequently prevent it; multiple open termux-boot issues report boot scripts not firing on newer Android. Do not rely on it as sole mechanism.

**3.6 Best current method to keep a long-running Python process alive (Samsung, non-root).** Layer all of:
1. `termux-wake-lock` (partial wake lock).
2. `rish -c 'dumpsys deviceidle whitelist +com.termux'` (Doze exemption; persists reboot).
3. `rish -c 'cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow'`.
4. Run the process under Termux with a persistent (ongoing) notification so Android treats the session as user-visible.
5. **Manual One UI steps (no shell equivalent):** add Termux to Battery → Background usage limits → **Never sleeping apps**; turn OFF "Put unused apps to sleep"; add Termux to Device care → Memory → Excluded apps; set Termux battery usage to "Unrestricted."
6. Optionally `termux-services` (runit) with `sv-enable` to auto-restart the process if it crashes.

**3.7 Auto-start after reboot given Shizuku needs re-pairing.** The honest constraint: **Termux:Boot can restart your Termux service, but it cannot restart Shizuku** (Shizuku needs the wireless-debugging start, requiring the Shizuku app + Developer options). So a boot script can bring up wake-lock + your Python daemon, but any rish-dependent step fails until you manually start Shizuku. Design your daemon to (a) start non-privileged functions at boot, and (b) lazily acquire rish privileges once Shizuku is up (poll `rish -c 'whoami'` and degrade gracefully when it returns non-zero).

### 4. HANDS-FREE / VOICE INPUT

**4.1 `termux-speech-to-text`** is the lowest-friction path: part of Termux:API, it invokes the Android system recognizer (Google), converts speech to text, and **streams partial matches to stdout** — pipe directly into Python (`text = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True).stdout`). It uses whatever recognizer is installed; with Google's on-device speech model it works offline/near-offline. Requires microphone permission for Termux:API. Because it offloads to the system recognizer, it adds ~0 persistent RAM — the right default given your llama-server budget.

**4.2 `termux-dialog`** offers interactive input dialogs; you can also use the Gboard voice key inside a `termux-dialog -t text` prompt to dictate — a robust fallback when `termux-speech-to-text` misbehaves.

**4.3 `am start` with RecognizerIntent from shell.** `android.speech.action.RECOGNIZE_SPEECH` **cannot be launched headlessly to return text to a script** — the platform requires `startActivityForResult` or a PendingIntent to receive results, which a bare `am start` cannot capture (per the official RecognizerIntent docs). Speech-recognizer apps like Kõnele expose service components invokable via `am start -n ee.ioc.phon.android.speak/...RECOGNIZE_SPEECH`, but returning text to a shell still needs the app's own plumbing. Net: use `termux-speech-to-text`, not raw `am`.

**4.4 Offline STT in Termux on ARM (RAM-constrained).** whisper.cpp compiles on aarch64 and runs tiny/base on CPU. Per the official ggerganov/whisper.cpp model card: **tiny = 75 MB disk / ~390 MB RAM; base = 142 MB / ~500 MB RAM** (uncompressed `ggml-tiny.bin` is ≈77.7 MB). Vosk is the better low-RAM choice: **vosk-model-small-en-us-0.15 is 41.2 MB on disk**, and Vosk's own docs (alphacephei.com/vosk) state the small model "is around 50 MB in size and requires about **300 MB of memory** in runtime," with lower latency (at some accuracy cost vs Whisper). Recommendation: for a phone already running llama-server on a 4 GB device, prefer `termux-speech-to-text` (system recognizer, ~0 extra RAM); reserve **Vosk small (~300 MB)** for fully-offline/no-Google operation, and treat **whisper.cpp tiny (~390 MB)** as the higher-accuracy-but-heavier option only when RAM headroom allows.

### 5. DENSE PYTHON PATTERNS (stdlib-only)

- **CLI dispatch:** For a frequently-invoked tool, a manual `sys.argv` dispatch dict is cheaper than `argparse` (argparse imports more and builds parser objects each run). Use argparse only when you need help text/validation. Keep the hot path import-light.
- **Import cost on ARM mobile:** `subprocess`, `argparse`, and `re` are relatively heavy; `json` is moderate. Defer expensive imports inside the function that needs them (lazy import) so cold-start of the common path stays fast. Avoid importing `re` if simple string methods suffice.
- **rish invocation from Python:** `subprocess.run(["rish","-c",cmd], capture_output=True, text=True, timeout=T)`; check `.returncode`, capture `.stdout`/`.stderr` separately; always set a timeout to avoid hangs when Shizuku is down.
- **Atomic JSONL appends:** open with `"a"`, write one `json.dumps(obj)+"\n"` per record; a single `write()` of a line under the pipe-buffer size (typically 4096 bytes on Linux/Android) is effectively atomic for concurrent `O_APPEND` writers. For larger/safer, use `fcntl.flock(f, LOCK_EX)` around the write.
- **File locking:** `fcntl.flock()` (advisory) for concurrent writers; wrap in try/finally to release.
- **Minimal HTTP endpoint:** `http.server.BaseHTTPRequestHandler` + `ThreadingHTTPServer` for a local control endpoint; bind to `127.0.0.1` only.
- **Cold-start latency:** minimize top-level imports; use `python -S` to skip site initialization if you don't need site-packages; keep the script small; avoid importing the whole tool for a subcommand.

### 6. SECURITY / RISK NOTES

**6.1 Shizuku permission scope.** Shizuku permission is **per-app** — each app must be individually approved in Shizuku, and Shizuku shows which apps hold access. Any app you grant Shizuku to can run anything at ADB `shell` (UID 2000) level: read logs, change secure settings, uninstall/disable packages for the user, simulate input, read many telemetry sources. Treat Shizuku access as granting broad device control to that app; grant it only to Termux and to shells you trust. `rish` grants the same privilege to *any* terminal app that can execute it, so protect the rish binary.

**6.2 Dangerous `settings put` keys.** `settings put` with WRITE_SECURE_SETTINGS can soft-brick or degrade the device. Highest-risk categories: `enabled_accessibility_services` (can lock you out if malformed), display density / font-scale keys (can make UI unusable), disabling critical System UI components, and `thermal_temp_state_value`-type tweaks (overriding thermal throttling risks overheating/hardware damage). Some misconfigurations require Safe Mode or factory reset to undo. Rule: never write a secure/global key whose default you can't name, and record the old value (`settings get …`) before changing it.

**6.3 Knox / warranty.** Using ADB and Shizuku via wireless debugging does **NOT** trip the Knox e-fuse or void warranty — the fuse trips only on bootloader unlock or rooting (Magisk/Sui). Multiple Samsung community and cross-community sources confirm ADB-level changes are warranty-safe; Sui (root Shizuku) *would* trip Knox. Secure Folder, Samsung Wallet/Pass, and Samsung Health continue to work under Shizuku/ADB (they break only when Knox is actually tripped). Knox, once tripped, is hardware-backed and generally irreversible without a mainboard replacement — so staying on the ADB/Shizuku path matters.

## Recommendations

**Stage 1 — Bring-up (once):**
1. Enable Developer options + Wireless debugging; pair and start Shizuku (§1.1).
2. Install `rish` into Termux and verify: `rish -c 'whoami'` must print `shell` (§1.2–1.3).
3. Grant Termux/Termux:API the standing permissions and exemptions:
   ```
   rish -c 'pm grant com.termux.api android.permission.WRITE_SECURE_SETTINGS'
   rish -c 'pm grant com.termux.api android.permission.READ_LOGS'
   rish -c 'dumpsys deviceidle whitelist +com.termux'
   rish -c 'dumpsys deviceidle whitelist +com.termux.api'
   rish -c 'cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow'
   ```
4. Do the manual One UI steps (§3.6 step 5) — these have no shell equivalent.

**Stage 2 — Telemetry rig:**
5. Probe readability once and branch your logger accordingly:
   ```
   rish -c 'cat /sys/class/power_supply/battery/current_now'   # expect a number (µA)
   rish -c 'cat /sys/class/power_supply/battery/voltage_now'   # µV
   rish -c 'cat /sys/class/thermal/thermal_zone0/temp'          # may be denied → fall back
   rish -c 'dumpsys thermalservice'                             # fallback for temps
   ```
6. Calibrate the battery-current sign/scale against a known load (screen-on discharge vs charging) before logging joules. Prefer `voltage_now × current_now` integration; cross-check with `charge_counter` deltas and `dumpsys batterystats`.

**Stage 3 — Persistence & voice:**
7. Boot script (`~/.termux/boot/start`): `termux-wake-lock` + launch your Python daemon; make rish steps lazy (poll `rish -c 'whoami'`).
8. Voice: default to `termux-speech-to-text` piped into Python; keep Vosk small (~300 MB) as the offline fallback given the RAM budget.

**Benchmarks that change the plan:**
- If `rish -c 'cat /sys/class/thermal/thermal_zone0/temp'` is denied → commit to `dumpsys thermalservice` parsing (and accept it may be empty; then rely on `dumpsys battery` temperature + the battery thermal zone).
- If reboots become frequent (>1–2/week) → the manual Shizuku restart cost dominates; consider a docked mini-PC or a one-command `adb` bring-up from a paired device.
- If llama-server + an offline STT model exceed the ~3.5 GB working budget → drop the local STT model, use the system recognizer only.

## Caveats
- **Version-dependent / could not fully verify:** exact AOSP `shell.te` grants for `sysfs_thermal` and `sysfs_devices_system_cpu` — thermal/CPU-freq readability at shell UID must be tested on the actual A15 One UI build. Battery sysfs read IS provably granted to the `shell` domain.
- **Samsung/MediaTek battery current sign and scale are device-specific** — do not assume the Linux canonical convention; measure it and validate against `POWER_SUPPLY_STATUS`.
- **No reliable shell command adds Termux to Samsung's "Never sleeping apps"** — treat as a manual GUI step.
- **Shizuku reboot restart has no verified fully-automated no-PC workaround** on the A15; community scripts exist but are unverified for this device.
- **`termux-speech-to-text` offline capability depends on the installed Google recognizer/language pack**; behavior varies by device and locale.
- **`dumpsys thermalservice` "Current temperatures from HAL" can be empty** on some devices even when the HAL is connected — confirm population on the A15.
- Several supporting sources are community write-ups (XDA, DEV.to, blogs); primary facts (rish syntax, SELinux labels, kernel ABI units, Termux add-on requirements, whisper/Vosk footprints, Knox behavior, Samsung sleep timers, A15 hardware) are corroborated by official docs (Shizuku-API, Termux GitHub, kernel.org, AOSP, Samsung developer/community, ggerganov/whisper.cpp, alphacephei.com/vosk, GSMArena).
