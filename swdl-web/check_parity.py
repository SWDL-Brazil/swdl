import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent / "messages"
LOCALES = ["pt-BR", "en", "es", "fr", "de", "it", "nl", "id", "ms"]

def flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flat(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flat(v, f"{prefix}.{i}"))
    else:
        out[prefix] = obj
    return out

base = flat(json.loads((ROOT / "pt-BR.json").read_text(encoding="utf-8-sig")))
print(f"pt-BR keys: {len(base)}")
ok = True
for loc in LOCALES:
    if loc == "pt-BR":
        continue
    data = flat(json.loads((ROOT / f"{loc}.json").read_text(encoding="utf-8-sig")))
    missing = [k for k in base if k not in data]
    extra = [k for k in data if k not in base]
    print(f"{loc}: {len(data)} missing={len(missing)} extra={len(extra)}")
    if missing:
        ok = False
        print("  missing sample:", missing[:5])
    if extra:
        ok = False
        print("  extra sample:", extra[:5])
print("PARITY_OK" if ok else "PARITY_FAIL")
sys.exit(0 if ok else 1)
