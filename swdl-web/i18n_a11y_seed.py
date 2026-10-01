"""Seed a11y.cvd_* keys into all 9 locales."""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent / "messages"
LOCALES = ["pt-BR", "en", "es", "fr", "de", "it", "nl", "id", "ms"]

T = {
    "a11y.cvd_label": {
        "pt-BR": "Modo daltonismo",
        "en": "Colorblind mode",
        "es": "Modo daltónico",
        "fr": "Mode daltonien",
        "de": "Farbenfehlsichtigkeit",
        "it": "Modalità daltonismo",
        "nl": "Kleurenblindmodus",
        "id": "Mode buta warna",
        "ms": "Mod buta warna",
    },
    "a11y.cvd_on": {
        "pt-BR": "Modo daltonismo ativado",
        "en": "Colorblind mode on",
        "es": "Modo daltónico activado",
        "fr": "Mode daltonien activé",
        "de": "Farbenfehlsichtigkeit aktiviert",
        "it": "Modalità daltonismo attiva",
        "nl": "Kleurenblindmodus aan",
        "id": "Mode buta warna aktif",
        "ms": "Mod buta warna aktif",
    },
    "a11y.cvd_off": {
        "pt-BR": "Modo daltonismo desativado",
        "en": "Colorblind mode off",
        "es": "Modo daltónico desactivado",
        "fr": "Mode daltonien désactivé",
        "de": "Farbenfehlsichtigkeit deaktiviert",
        "it": "Modalità daltonismo disattiva",
        "nl": "Kleurenblindmodus uit",
        "id": "Mode buta warna nonaktif",
        "ms": "Mod buta warna mati",
    },
}


def set_path(obj, path, value):
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def get_path(obj, path):
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def main():
    for loc in LOCALES:
        path = ROOT / f"{loc}.json"
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        updated = 0
        for key, by_loc in T.items():
            if loc in by_loc and get_path(data, key) is None:
                set_path(data, key, by_loc[loc])
                updated += 1
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{loc}: +{updated}")


if __name__ == "__main__":
    main()
