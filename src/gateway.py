#!/usr/bin/env python3
"""gateway.py — File-currency gateway: run a black-box app, intercept its output currency,
stamp a face-value card (area + entropy + sha), store it, append a ledger entry, verify.

App spec (JSON): {"name": "...", "cmd": "curl -sL -o {out} {url}", "ext": "html", "coeff_override": null}
The command must be a local shell template; remote hosts are pluggable via cmd prefixes.
"""
import argparse, hashlib, json, os, subprocess, sys, time, zlib

COEFF = {".md": 1.0, ".txt": 1.0, ".html": 3.0, ".json": 1.2, ".png": 20.0, ".jpg": 20.0,
         ".mp4": 100.0, ".zip": 50.0, ".apk": 60.0, ".pdf": 10.0, ".csv": 1.5}
DEFAULT = 10.0


def face(path):
    st = os.stat(path)
    ext = os.path.splitext(path.lower())[1]
    c = COEFF.get(ext, DEFAULT)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(4 << 20), b""):
            h.update(b)
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    ratio = (len(zlib.compress(head, 1)) / len(head)) if head else 0
    return {"bytes": st.st_size, "ext": ext, "coeff": c, "area": round(c * st.st_size, 1),
            "entropy_density": round(ratio, 3), "sha256": h.hexdigest()[:16]}


def settle(app, url, store, name_prefix="currency"):
    os.makedirs(store, exist_ok=True)
    ext = app.get("ext", "bin")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_name = f"{name_prefix}@{stamp}.{ext}"
    out = os.path.join(store, out_name)
    cmd = app["cmd"].format(out=out, url=url)
    print(f"[gateway] input: {url}")
    print(f"[gateway] app: {app['name']} · cmd: {cmd[:80]}")
    subprocess.run(cmd, shell=True, timeout=app.get("timeout", 120))
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        print("[gateway] no currency produced"); return None
    card = {"time": time.strftime("%F %T"), "app": app["name"], "input": url,
            "output": out, **face(out), "status": "settled"}
    json.dump(card, open(out + ".face.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(store, "currencies.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(card, ensure_ascii=False) + "\n")
    print(f"[gateway] intercepted: {out_name}  {card['bytes']:,} B")
    print(f"[gateway] face: {card['area']:,.0f} byte-eq · coeff {card['coeff']} · entropy {card['entropy_density']} · sha {card['sha256']}")
    return card


def verify(card_file):
    card = json.load(open(card_file, encoding="utf-8"))
    now = face(card["output"])
    ok = now["sha256"] == card["sha256"] and now["area"] == card["area"]
    print(("OK face-value intact" if ok else "MISMATCH tampered") +
          f"  sha {now['sha256']}  area {now['area']:,.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="File-currency gateway")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("settle"); s.add_argument("--app", required=True, help="app spec JSON file")
    s.add_argument("--url", required=True); s.add_argument("--store", required=True); s.add_argument("--name", default="currency")
    v = sub.add_parser("verify"); v.add_argument("--card", required=True)
    a = ap.parse_args()
    if a.cmd == "settle":
        settle(json.load(open(a.app, encoding="utf-8")), a.url, a.store, a.name)
    else:
        verify(a.card)
