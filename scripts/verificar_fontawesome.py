#!/usr/bin/env python
"""Checklist de verificación — Font Awesome local (solo dev)."""

import sys
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(condition, message, details=""):
    symbol = f"{GREEN}✅{RESET}" if condition else f"{RED}❌{RESET}"
    status = f"{GREEN}OK{RESET}" if condition else f"{RED}FALLA{RESET}"

    print(f"{symbol} {message:<50} [{status}]")
    if details:
        print(f"   {YELLOW}→ {details}{RESET}")

    return condition


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}🎨 VERIFICACIÓN DE FONT AWESOME LOCAL{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

    static_dir = root / "despacho_django" / "static"
    templates_dir = root / "despacho_django" / "templates"
    fa_dir = static_dir / "fontawesome"

    all_good = True

    print(f"\n{BOLD}1. ARCHIVOS FONT AWESOME{RESET}")
    print("-" * 70)

    fa_files = {
        "css/all.min.css": "CSS Principal",
        "css/solid.min.css": "CSS Sólidos",
        "css/brands.min.css": "CSS Marcas",
        "webfonts/fa-solid-900.woff2": "Fuente Sólida",
        "webfonts/fa-brands-400.woff2": "Fuente Marcas",
        "webfonts/fa-regular-400.woff2": "Fuente Regular",
        "webfonts/fa-v4compatibility.woff2": "Compatibilidad v4",
    }

    for file_path, description in fa_files.items():
        full_path = fa_dir / file_path
        exists = full_path.exists()
        all_good &= check(exists, f"  {description:<35}", file_path)
        if exists:
            size_kb = full_path.stat().st_size / 1024
            print(f"       Tamaño: {size_kb:.1f} KB")

    print(f"\n{BOLD}2. TEMPLATES Y HERENCIA{RESET}")
    print("-" * 70)

    templates = {
        "base.html": "Template base (debe existir)",
        "index.html": "Debe extender base.html",
        "proyectos.html": "Debe extender base.html",
        "contacto.html": "Debe extender base.html",
        "sobre-nosotros.html": "Debe extender base.html",
    }

    for tmpl_name, description in templates.items():
        tmpl_path = templates_dir / tmpl_name
        exists = tmpl_path.exists()
        all_good &= check(exists, f"  {tmpl_name:<30}", description)

    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")

    if all_good:
        print(f"{GREEN}{BOLD}✅ VERIFICACIÓN EXITOSA{RESET}")
    else:
        print(f"{RED}{BOLD}❌ FALLOS DETECTADOS{RESET}")

    print(f"\n{BLUE}{'='*70}{RESET}\n")

    return 0 if all_good else 1


if __name__ == "__main__":
    raise SystemExit(main())
