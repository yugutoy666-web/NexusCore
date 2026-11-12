#!/system/bin/sh
# rescue.sh — executed by the external immune host via `adb shell`.
# Contract: two independent criteria (heartbeat pid alive + ports open) -> restart only what's dead.
# RULE: variable names must be ASCII (mksh drops/executes non-ASCII assignments silently).
WORLD="$1"
RT="${RT:-/data/local/tmp/rt/python/bin/python3}"
RTN="${RTN:-/data/local/tmp/rt/runtime/bin/node}"
export LD_LIBRARY_PATH=/data/local/tmp/rt/runtime/lib
export OPENSSL_CONF=/dev/null
cd "$WORLD" || exit 1
MSG=""
PID=$(tail -1 0.引擎/核/心跳.tsv 2>/dev/null | cut -f2)
CORE_ALIVE=0
if [ -n "$PID" ] && [ -d "/proc/$PID" ]; then CORE_ALIVE=1; fi
port_open() { grep -qi ":$1 " /proc/net/tcp /proc/net/tcp6 2>/dev/null; }
P3296=0
P8767=0
if port_open 0CE0; then P3296=1; fi
if port_open 223F; then P8767=1; fi
MSG="$MSG core=$CORE_ALIVE 3296=$P3296 8767=$P8767"
if [ "$CORE_ALIVE" = "0" ]; then
  (setsid "$RT" 0.引擎/核/核.py --loop >>0.引擎/核/核.out 2>&1 &)
  MSG="$MSG start-core"
fi
if [ "$P3296" = "0" ]; then
  (setsid "$RT" 0.引擎/挂载/根台.py 3296 >>0.引擎/挂载/根台.log 2>&1 &)
  MSG="$MSG start-root"
fi
if [ "$P8767" = "0" ]; then
  (setsid "$RTN" 0.引擎/网盘/网盘.js >>0.引擎/网盘/网盘.out 2>&1 &)
  MSG="$MSG start-disk"
fi
sleep 2
if "$RT" 0.引擎/核/复位.py >/dev/null 2>&1; then
  MSG="$MSG reset-ok"
else
  MSG="$MSG reset-fail"
fi
echo "rescue:$MSG"
