#!/usr/bin/env python
import os
import sys
from pathlib import Path

import django
import requests


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"

    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    django.setup()

    try:
        response = requests.get("http://127.0.0.1:8000/api/proyectos/?page_size=5", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data.get('count')}")
            print(f"Results: {len(data.get('results', []))}")
            if data.get("results"):
                print("Primer proyecto:", data["results"][0]["nombre"])
            else:
                print("No hay resultados")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error conectando a la API: {e}")


if __name__ == "__main__":
    main()
