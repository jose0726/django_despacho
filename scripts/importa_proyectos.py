import os
import sys
import json
from pathlib import Path
from time import perf_counter

"""IMPORTANTE: este script borra todos los proyectos y los reimporta.
Úsalo solo en entornos controlados (dev/staging).
"""


def resolve_paths():
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"  # donde está manage.py
    return root, project_dir


ROOT, PROJECT_DIR = resolve_paths()

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")

import django  # noqa: E402

django.setup()


def normalize_category(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    return " ".join(s.split()).lower()


def normalize_subcategory(value: str) -> str:
    s = (value or "").strip()
    return s.lower()


def pick_first_valid_image(images) -> str | None:
    if not images:
        return None
    for img in images:
        if isinstance(img, str) and img.strip():
            return img.strip()
    return None


def locate_json_file() -> Path:
    candidates = [
        PROJECT_DIR / "proyectos.json",
        ROOT / "proyectos.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"No se encontró proyectos.json en: {', '.join(str(c) for c in candidates)}"
    )


def main():
    from django.apps import apps

    Proyecto = apps.get_model("proyectos", "Proyecto")
    t0 = perf_counter()

    json_path = locate_json_file()
    print(f"[INFO] Usando JSON: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        print("[WARN] El JSON no es una lista. Nada que importar.")
        return

    print(f"[INFO] Registros en JSON: {len(raw)}")

    prev_count = Proyecto.objects.count()
    if prev_count:
        Proyecto.objects.all().delete()
        print(f"[INFO] Eliminados {prev_count} proyectos existentes.")
    else:
        print("[INFO] No había proyectos previos que eliminar.")

    seen_names = set()
    to_create: list = []

    for idx, p in enumerate(raw, start=1):
        nombre = (p.get("titulo") or "").strip()
        if not nombre:
            continue

        name_key = nombre.lower()
        if name_key in seen_names:
            continue
        seen_names.add(name_key)

        descripcion = (p.get("descripcion") or "").strip()
        categoria = normalize_category(p.get("categoria") or "")
        subcategoria = normalize_subcategory(p.get("sub") or "")
        imagen = pick_first_valid_image(p.get("imagenes"))

        to_create.append(
            Proyecto(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                subcategoria=subcategoria,
                imagen=imagen or None,
            )
        )

        if idx % 200 == 0:
            print(f"[INFO] Procesados {idx} elementos del JSON...")

    print(f"[INFO] A crear (tras normalizar y deduplicar por nombre): {len(to_create)}")

    if to_create:
        Proyecto.objects.bulk_create(to_create, batch_size=1000)
        print(f"[OK] Importados {len(to_create)} proyectos.")
    else:
        print("[INFO] No hay proyectos para importar.")

    t1 = perf_counter()
    print(f"[DONE] ¡Importación completa! Tiempo total: {t1 - t0:.2f}s")


if __name__ == "__main__":
    main()
