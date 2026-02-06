from __future__ import annotations

from django.http import JsonResponse
from django.views.csrf import csrf_failure as default_csrf_failure


def csrf_failure(request, reason=""):
    """Return JSON for CSRF failures on JSON endpoints (e.g. /contact/)."""
    accept = (request.headers.get("Accept") or "").lower()
    content_type = (request.headers.get("Content-Type") or "").lower()

    wants_json = (
        request.path.startswith("/contact")
        or "application/json" in accept
        or "application/json" in content_type
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )

    if wants_json:
        return JsonResponse(
            {
                "ok": False,
                "error": "CSRF verification failed.",
                "reason": reason or "",
            },
            status=403,
        )

    return default_csrf_failure(request, reason=reason)
