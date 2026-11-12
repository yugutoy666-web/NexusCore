#!/usr/bin/env python3
"""app_model.py — Apps as black-box macro-nodes (App_Model schema + scheduler matching).

An app declares only: inputs contracts, outputs contracts, env, runtime metrics, status,
entry command, probe. Dependency scanning is intentionally avoided ("dependency hell").
"""
import argparse, json, os, socket, subprocess, sys, time

SPEC_FIELDS = ("name", "type", "host", "inputs", "outputs", "env", "runtime_metrics",
               "status", "entry", "probe", "mode")


def gen(specs, out):
    os.makedirs(out, exist_ok=True)
    for a in specs:
        m = {**a, "status": a.get("status", "Unknown"), "generated": time.strftime("%F %T")}
        d = os.path.join(out, str(a["name"]))
        os.makedirs(d, exist_ok=True)
        json.dump(m, open(os.path.join(d, "-1(App_Model)[spec].json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print(f"generated {len(specs)} app models -> {out}")


def load_all(out):
    models = []
    for name in sorted(os.listdir(out)):
        p = os.path.join(out, name, "-1(App_Model)[spec].json")
        if os.path.exists(p):
            models.append(json.load(open(p, encoding="utf-8")))
    return models


def probe_status(m):
    pr = m.get("probe") or {}
    if "port" in pr:
        s = socket.socket(); s.settimeout(0.6)
        try:
            return "Running" if s.connect_ex(("127.0.0.1", int(pr["port"]))) == 0 else "Stopped"
        finally:
            s.close()
    if "file" in pr:
        p = pr["file"]
        if not os.path.exists(p):
            return "Stopped"
        age = time.time() - os.path.getmtime(p)
        return "Running" if age <= pr.get("fresh_sec", 400000) else "Stopped"
    return "Unknown" if m.get("mode") != "on-demand" else "Ready"


def match(models, need):
    words = [w for w in need.lower().split() if w]
    scored = []
    for m in models:
        text = " ".join(m.get("inputs", []) + m.get("outputs", []) + [m.get("host", "")]).lower()
        sc = sum(2 for w in words if w in text)
        st = probe_status(m)
        if st in ("Running", "Ready"):
            sc += 1
        scored.append((sc, m, st))
    scored.sort(key=lambda x: -x[0])
    print(f"need: {need}\n{'score':<6}{'app':<14}{'status':<10}entry")
    for sc, m, st in scored[:4]:
        print(f"{sc:<6}{m['name']:<14}{st:<10}{m.get('entry','')[:60]}")
    return scored


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="App black-box models")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--spec", required=True, help="JSON list of app specs"); g.add_argument("--out", default="./apps")
    l = sub.add_parser("list"); l.add_argument("--out", default="./apps")
    mt = sub.add_parser("match"); mt.add_argument("--apps", default="./apps"); mt.add_argument("--need", required=True)
    a = ap.parse_args()
    if a.cmd == "gen":
        gen(json.load(open(a.spec, encoding="utf-8")), a.out)
    elif a.cmd == "list":
        for m in load_all(a.out):
            print(f"{m['name']:<14}{probe_status(m):<10}{m.get('entry','')[:60]}")
    else:
        match(load_all(a.apps), a.need)
