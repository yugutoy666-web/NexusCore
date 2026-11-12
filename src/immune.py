#!/usr/bin/env python3
"""immune.py — External (out-of-band) immunity for an agent that lives on another device.

Doctrine: "monitoring from the same layer is not monitoring".
This runs on an always-on host, probes a peer (e.g. an Android phone) over adb,
checks *two independent criteria* (heartbeat freshness + listening ports),
executes a rescue script when needed, scans for runaway processes and kills only
whitelisted "own" processes — every action is logged.

Config (JSON):
{
  "peer": {"transport":"adb", "serial":"auto",
           "heartbeat_file":"/sdcard/world/engine/heartbeat.txt",
           "ports":{"0CD0":3280,"0CE0":3296,"223F":8767},
           "rescue_script":"/sdcard/world/rescue.sh"},
  "threshold_sec": 120,
  "whitelist":["system_server","systemui","com.android","com.tencent","com.miui"],
  "own_markers":["core.py","daemon.sh"],
  "forbid_markers":["immune","rescue","--once"],
  "ledger":"/var/log/nexuscore/immunity.tsv"
}
"""
import argparse, json, os, subprocess, sys, time


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return (p.stdout or "").strip(), (p.stderr or "").strip(), p.returncode
    except Exception as e:
        return "", f"EXC {e}", -1


def log(cfg, *fields):
    led = cfg.get("ledger", "/var/log/nexuscore/immunity.tsv")
    os.makedirs(os.path.dirname(led), exist_ok=True)
    with open(led, "a", encoding="utf-8") as f:
        f.write("\t".join(str(x) for x in [time.strftime("%F %T"), *fields]) + "\n")


def discover_serial(cfg):
    peer = cfg["peer"]
    serial = peer.get("serial", "auto")
    if serial and serial != "auto":
        return serial
    out, _, _ = sh("adb devices 2>/dev/null")
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device" and ":" in parts[0]:
            return parts[0]  # wireless peer preferred
    return None


def heartbeat_age(cfg, serial):
    hb = cfg["peer"].get("heartbeat_file")
    if not hb:
        return None
    out, _, _ = sh(f'adb -s {serial} shell "cat {hb} 2>/dev/null"')
    if not out:
        return None
    try:
        return int(time.time() - int(out.strip().splitlines()[-1]))
    except ValueError:
        return None


def open_ports(cfg, serial):
    out, _, _ = sh(f'adb -s {serial} shell "cat /proc/net/tcp /proc/net/tcp6 2>/dev/null"', 40)
    mapping = {k.upper(): v for k, v in (cfg["peer"].get("ports") or {}).items()}
    found = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) > 3 and parts[3] == "0A":
            hexport = parts[1].split(":")[-1].upper()
            if hexport in mapping:
                found.add(int(mapping[hexport]))
    return found


def rescue(cfg, serial):
    script = cfg["peer"].get("rescue_script")
    if not script:
        return "no-rescue-script"
    out, _, rc = sh(f'adb -s {serial} shell "sh {script}"', 180)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return f"rc={rc}" + ((" | " + " ".join(lines[-2:])) if lines else "")


def cancer_scan(cfg, serial):
    out, _, _ = sh(f'adb -s {serial} shell "ps -A -o pid,ppid,%cpu,rss,args 2>/dev/null"', 40)
    if not out:
        return []
    rows = []
    for line in out.splitlines():
        c = line.split(None, 4)
        if len(c) == 5 and c[0].isdigit():
            rows.append(c)
    names = {}
    for c in rows:
        names[c[4][:40]] = names.get(c[4][:40], 0) + 1
    hits = []
    for pid, ppid, cpu, rss, cmd in rows:
        if any(w in cmd for w in cfg.get("whitelist", [])):
            continue
        if not any(w in cmd for w in cfg.get("own_markers", [])):
            continue
        if any(w in cmd for w in cfg.get("forbid_markers", [])):
            continue
        try:
            cpu_f = float(cpu)
        except ValueError:
            cpu_f = 0
        try:
            rss_mb = int(rss) // 1024
        except ValueError:
            rss_mb = 0
        reason = None
        if names.get(cmd[:40], 0) > 3:
            reason = f"duplicate x{names[cmd[:40]]}"
        elif cpu_f > 30:
            reason = f"cpu {cpu_f:.0f}%>30"
        elif rss_mb > 800:
            reason = f"rss {rss_mb}MB>800"
        if reason:
            hits.append((pid, reason, cmd[:80]))
    return hits


def tick(cfg):
    serial = discover_serial(cfg)
    if not serial:
        log(cfg, "offline", "peer not reachable (wait & retry)")
        print("peer offline -> logged"); return
    age = heartbeat_age(cfg, serial)
    missing = set(int(p) for p in (cfg["peer"].get("ports") or {}).values()) - open_ports(cfg, serial)
    threshold = cfg.get("threshold_sec", 120)
    need_rescue = (age is None) or (age > threshold) or bool(missing)
    if need_rescue:
        why = f"heartbeat={age}s" if age is not None else "heartbeat=unreadable"
        if missing:
            why += f" missing_ports={sorted(missing)}"
        log(cfg, "rescue", why)
        print(f"WARN {why} -> defibrillate:", rescue(cfg, serial))
    else:
        print(f"OK heartbeat={age}s ports={sorted(open_ports(cfg, serial))}")
    for pid, reason, cmd in cancer_scan(cfg, serial):
        sh(f'adb -s {serial} shell "kill -9 {pid} 2>/dev/null"', 20)
        log(cfg, "kill", serial, pid, reason, cmd)
        print(f"KILL {pid} {reason} {cmd[:60]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="External immunity")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick"); t.add_argument("--config", required=True)
    l = sub.add_parser("ledger"); l.add_argument("--config", required=True); l.add_argument("-n", type=int, default=10)
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    if a.cmd == "tick":
        tick(cfg)
    else:
        p = cfg.get("ledger")
        print("\n".join(open(p, encoding="utf-8").read().splitlines()[-a.n:]) if p and os.path.exists(p) else "no ledger")
