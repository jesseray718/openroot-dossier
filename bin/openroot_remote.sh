#!/usr/bin/env bash
set -uo pipefail
CORE="${CORE_IP:-100.122.169.43}"
USER="jesse"
CMD="${*:-echo no command given}"
echo "[remote] $USER@$CORE :: $CMD"
ssh -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new \
    -o BatchMode=yes "\( {USER}@ \){CORE}" "cd \$HOME/openroot && $CMD"
