import os
import sys
import subprocess


def run_manage_py(*args: str) -> None:
    subprocess.check_call([sys.executable, "despacho_django/manage.py", *args])


def main() -> None:
    # Run migrations and collect static assets on deploy/start.
    # This ensures STATIC_ROOT exists before WhiteNoise initializes.
    run_manage_py("migrate", "--noinput")
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
