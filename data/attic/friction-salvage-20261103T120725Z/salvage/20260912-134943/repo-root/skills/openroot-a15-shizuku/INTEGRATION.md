# Integration Notes
- sisters: une-joule-native, openroot-two-pane, openroot-seed-oracle, openroot-integration
- pane rule: A15 only. Never paste rish blocks into jesse@optiplex3060.
- inbound: seed-oracle and une joule probes ask for sysfs + dumpsys
- outbound: rish wrappers that return None and continue
- anti-patterns: hard-fail when rish is down; start privileged work before Shizuku is confirmed
- proof: test -s /home/workdir/.grok/skills/openroot-a15-shizuku/scripts/hive_entry.py
