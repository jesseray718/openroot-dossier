#!/data/data/com.termux/files/usr/bin/bash
# RUN ON THE A15 (Termux). Requires: pkg install termux-boot
# Survives reboots: ollama tunnel + syncthing serve + daily pod verify.
set -euo pipefail
BOOTRC="$HOME/.termux/boot"
mkdir -p "$BOOTRC"

# tunnel: forward optiplex ollama 11434 with auto-reconnect loop
cat > "$BOOTRC/ollama-tunnel" <<'TUN'
#!/data/data/com.termux/files/usr/bin/bash
TERMUX_WIFI_LOCK=wifi-lock termux-wake-lock
while true; do
  ssh -NT -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 -o ConnectTimeout=15 \
    -L 127.0.0.1:11434:127.0.0.1:11434 jesse@100.122.169.43
  sleep 20
done
TUN
chmod +x "$BOOTRC/ollama-tunnel"

# syncthing: serve the mesh under the wake lock
cat > "$BOOTRC/syncthing-serve" <<'SRV'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
exec "$HOME/syncthing/syncthing" serve
SRV
chmod +x "$BOOTRC/syncthing-serve"
echo "installed: $BOOTRC/ollama-tunnel $BOOTRC/syncthing-serve"
echo "next reboot, both come up automatically. Test now:"
echo "  bash \$HOME/.termux/boot/ollama-tunnel & bash \$HOME/.termux/boot/syncthing-serve &"
