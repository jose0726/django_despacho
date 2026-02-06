import json
import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def manage_py_path() -> Path:
    """Find manage.py for both common layouts.

    Supports:
      - /app/manage.py
      - /app/despacho_django/manage.py
    """

    candidates = [
        repo_root() / "manage.py",
        repo_root() / "despacho_django" / "manage.py",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "No se encontró manage.py. Busqué en: " + ", ".join(str(c) for c in candidates)
    )


def project_dir() -> Path:
    """Directory that contains manage.py."""

    return manage_py_path().parent


def ensure_project_on_syspath() -> None:
    """Ensure Django project directory is importable in *this* process."""

    p = project_dir()
    ps = str(p)
    if ps not in sys.path:
        sys.path.insert(0, ps)


def ensure_project_on_pythonpath_env() -> None:
    """Ensure Django project directory is importable for subprocesses (gunicorn)."""

    p = str(project_dir())
    current = os.environ.get("PYTHONPATH", "")
    parts = [x for x in current.split(os.pathsep) if x]
    if p not in parts:
        parts.insert(0, p)
        os.environ["PYTHONPATH"] = os.pathsep.join(parts)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def run_manage_py(*args: str) -> None:
    ensure_project_on_pythonpath_env()
    subprocess.check_call([sys.executable, str(manage_py_path()), *args])


def ensure_superuser_if_requested() -> None:
    """Optionally create a Django superuser at boot.

    This is helpful on Railway when you can't find/enable the Shell.

    Enable by setting:
      - CREATE_SUPERUSER=true
      - DJANGO_SUPERUSER_USERNAME
      - DJANGO_SUPERUSER_EMAIL (optional)
      - DJANGO_SUPERUSER_PASSWORD

    Idempotent: if the user exists, it does nothing.
    """

    if not env_bool("CREATE_SUPERUSER", default=False):
        return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()

    if not username or not password:
        print("CREATE_SUPERUSER=true but missing DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD")
        return

    ensure_project_on_syspath()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    import django

    django.setup()
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists; skipping")
        return

    User.objects.create_superuser(username=username, email=email or None, password=password)
    print(f"Superuser '{username}' created")


def seed_projects_if_requested() -> None:
    """Optionally seed Proyecto rows from proyectos.json.

    Useful when production DB starts empty and you want the Proyectos page to
    show content immediately.

    Enable by setting:
      - SEED_PROJECTS=true

    Optional:
      - SEED_PROJECTS_FORCE=true  (deletes existing Proyecto rows first)

    Notes:
      - This seeds only basic fields (nombre/descripcion/categoria/subcategoria).
      - Images are not imported; the frontend will show placeholders until you
        upload images or configure a media storage.
    """

    if not env_bool("SEED_PROJECTS", default=False):
        return

    ensure_project_on_syspath()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    import django

    django.setup()

    from django.apps import apps

    Proyecto = apps.get_model("proyectos", "Proyecto")
    force = env_bool("SEED_PROJECTS_FORCE", default=False)

    existing = Proyecto.objects.count()
    if existing and not force:
        print(f"SEED_PROJECTS=true but Proyecto already has {existing} rows; skipping")
        return

    # Locate JSON in a couple of likely places inside the repo.
    root = repo_root()
    candidates = [
        # common in this repo
        root / "despacho_django" / "proyectos.json",
        root / "despacho_django" / "static" / "js" / "proyectos.json",
        # alternate layout
        root / "proyectos.json",
        project_dir() / "proyectos.json",
        project_dir() / "static" / "js" / "proyectos.json",
    ]
    json_path = next((p for p in candidates if p.exists()), None)
    if not json_path:
        print("SEED_PROJECTS=true but proyectos.json not found; skipping")
        return

    if force and existing:
        Proyecto.objects.all().delete()
        print(f"[SEED] Deleted {existing} existing Proyecto rows")

    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list) or not raw:
        print("[SEED] proyectos.json is empty or invalid; skipping")
        return

    def norm(s: str) -> str:
        return " ".join((s or "").strip().split())

    to_create = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        nombre = norm(item.get("titulo") or item.get("nombre") or "")
        if not nombre:
            continue
        key = nombre.lower()
        if key in seen:
            continue
        seen.add(key)

        categoria = norm(item.get("categoria") or "")
        subcategoria = norm(item.get("sub") or item.get("subcategoria") or "")
        descripcion = norm(item.get("descripcion") or "")

        to_create.append(
            Proyecto(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                subcategoria=subcategoria,
                imagen=None,
            )
        )

    if not to_create:
        print("[SEED] No Proyecto rows to create after parsing JSON")
        return

    Proyecto.objects.bulk_create(to_create, batch_size=500)
    print(f"[SEED] Created {len(to_create)} Proyecto rows")


def main() -> None:
    # Run migrations and collect static assets on deploy/start.
    # This ensures STATIC_ROOT exists before WhiteNoise initializes.
    # Make imports consistent for subprocesses too.
    ensure_project_on_pythonpath_env()

    # Run migrations and collect static assets before starting Gunicorn.
    run_manage_py("migrate", "--noinput")
    ensure_superuser_if_requested()
    seed_projects_if_requested()
    run_manage_py("collectstatic", "--noinput")

    port = os.getenv("PORT", "8080")
    workers = os.getenv("WEB_CONCURRENCY", "2")
    timeout = os.getenv("GUNICORN_TIMEOUT", "60")

    args = [
        "gunicorn",
        "despacho_django.wsgi:application",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        str(workers),
        "--timeout",
        str(timeout),
        # Railway-friendly logs
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--log-level",
        os.getenv("GUNICORN_LOG_LEVEL", "info"),
        "--capture-output",
    ]

    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
