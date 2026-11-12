#!/usr/bin/env python3
"""area.py — Compute-Equivalent Area: sizing, face values, and the streaming read gate.

Area = protocol_coefficient * bytes. It measures *compute-equivalent* (production cost),
NOT information entropy. Entropy density must be measured separately (zlib ratio).
"""
import argparse, hashlib, json, os, sys, time, zlib

COEFF = {
    ".md": 1.0, ".txt": 1.0, ".log": 1.0, ".json": 1.2, ".jsonl": 1.2, ".csv": 1.5, ".tsv": 1.5,
    ".html": 3.0, ".css": 3.0, ".yml": 3.0, ".yaml": 3.0, ".toml": 3.0, ".ini": 3.0, ".conf": 3.0,
    ".py": 5.0, ".js": 5.0, ".ts": 5.0, ".sh": 5.0, ".java": 5.0, ".c": 5.0, ".cpp": 5.0,
    ".go": 5.0, ".rs": 5.0, ".sql": 5.0, ".svg": 5.0,
    ".pdf": 10.0, ".docx": 8.0, ".xlsx": 8.0, ".pptx": 8.0,
    ".png": 20.0, ".jpg": 20.0, ".jpeg": 20.0, ".gif": 20.0, ".webp": 20.0, ".bmp": 20.0,
    ".mp3": 40.0, ".wav": 40.0, ".flac": 40.0, ".m4a": 40.0, ".ogg": 40.0,
    ".mp4": 100.0, ".mov": 100.0, ".avi": 100.0, ".mkv": 100.0, ".webm": 100.0,
    ".zip": 50.0, ".tar": 50.0, ".gz": 50.0, ".tgz": 50.0, ".7z": 50.0, ".rar": 50.0,
    ".apk": 60.0, ".dex": 60.0, ".jar": 60.0,
    ".safetensors": 200.0, ".gguf": 200.0, ".pt": 200.0, ".pth": 200.0, ".onnx": 200.0,
    ".bin": 20.0, ".pkl": 150.0, ".npz": 150.0, ".npy": 150.0,
}
DEFAULT_COEFF = 10.0


def coeff_of(path: str) -> float:
    return COEFF.get(os.path.splitext(path.lower())[1], DEFAULT_COEFF)


def face_value(path: str) -> dict:
    st = os.stat(path)
    c = coeff_of(path)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    ratio = (len(zlib.compress(head, 1)) / len(head)) if head else 0.0
    return {"bytes": st.st_size, "coeff": c, "area": c * st.st_size,
            "entropy_density": round(ratio, 3), "sha256": h.hexdigest()[:16]}


def scan(root: str) -> dict:
    total_bytes = files = dirs = 0
    by_ext = {}
    for cur, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "node_modules", "__pycache__")]
        dirs += 1
        for name in fs:
            p = os.path.join(cur, name)
            try:
                st = os.stat(p)
            except OSError:
                continue
            ext = os.path.splitext(name.lower())[1] or "(none)"
            c = COEFF.get(ext, DEFAULT_COEFF)
            e = by_ext.setdefault(ext, {"files": 0, "bytes": 0, "area": 0.0, "coeff": c})
            e["files"] += 1
            e["bytes"] += st.st_size
            e["area"] += c * st.st_size
            total_bytes += st.st_size
            files += 1
    area = sum(e["area"] for e in by_ext.values())
    return {"root": root, "files": files, "dirs": dirs, "bytes": total_bytes,
            "area": area, "amplification": round(area / max(total_bytes, 1), 2),
            "by_ext": by_ext}


def safe_read(path: str, limit_kb: float = 1000.0, chunk_mb: int = 1) -> dict:
    """Read gate: compute area first; above threshold -> stream (never load whole file)."""
    st = os.stat(path)
    area_kb = coeff_of(path) * st.st_size / 1024.0
    stream = area_kb > limit_kb
    h, read, blocks = hashlib.sha256(), 0, 0
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_mb << 20)
            if not b:
                break
            h.update(b); read += len(b); blocks += 1
    return {"path": path, "bytes": st.st_size, "area_kb": round(area_kb, 1),
            "streamed": stream, "blocks": blocks, "sha256": h.hexdigest()[:16]}


def cmd_report(a):
    s = scan(a.root)
    print(f"# Area audit · {s['root']}\n")
    print(f"- files: {s['files']:,}   dirs: {s['dirs']:,}")
    print(f"- physical: {s['bytes']:,} B = {s['bytes']/1e9:.2f} GB")
    print(f"- AREA: {s['area']:,.0f} byte-equivalent = {s['area']/1e9:,.2f} GB-eq ({s['amplification']}x)")
    rows = sorted(s["by_ext"].items(), key=lambda kv: -kv[1]["area"])[:15]
    print("\n| ext | files | bytes | coeff | area | share |")
    print("|---|---|---|---|---|---|")
    for ext, e in rows:
        print(f"| {ext} | {e['files']:,} | {e['bytes']:,} | {e['coeff']:.0f} | {e['area']:,.0f} | {100*e['area']/max(s['area'],1):.1f}% |")
    if a.json:
        json.dump(s, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cmd_read(a):
    print(json.dumps({**face_value(a.file), **safe_read(a.file, a.limit_kb)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Compute-Equivalent Area toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report"); r.add_argument("--root", required=True); r.add_argument("--json")
    r.set_defaults(fn=cmd_report)
    rd = sub.add_parser("read"); rd.add_argument("--file", required=True)
    rd.add_argument("--limit-kb", type=float, default=1000.0); rd.set_defaults(fn=cmd_read)
    args = ap.parse_args(); args.fn(args)
