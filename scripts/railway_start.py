import os
import sys
import subprocess


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def run_manage_py(*args: str) -> None:
    subprocess.check_call([sys.executable, "despacho_django/manage.py", *args])


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


def main() -> None:
    # Run migrations and collect static assets on deploy/start.
    # This ensures STATIC_ROOT exists before WhiteNoise initializes.
    run_manage_py("migrate", "--noinput")
    ensure_superuser_if_requested()
    run_manage_py("collectstatic", "--noinput")

    port = os.getenv("PORT", "8080")
    workers = os.getenv("WEB_CONCURRENCY", "2")
    timeout = os.getenv("GUNICORN_TIMEOUT", "60")

    args = [
        "gunicorn",
        "despacho_django.wsgi:application",
        "--chdir",
        "despacho_django",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        str(workers),
        "--timeout",
        str(timeout),
    ]

    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
