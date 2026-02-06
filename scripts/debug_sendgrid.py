from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from python_http_client.exceptions import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    load_dotenv(env_path)

    key = os.getenv("SENDGRID_API_KEY")
    print("SENDGRID_API_KEY loaded:", bool(key), "prefix:", (key[:3] if key else None))

    if not key:
        print(f"Missing SENDGRID_API_KEY in {env_path}")
        return 2

    msg = Mail(
        from_email="ccjose088@gmail.com",
        to_emails="ccjose088@gmail.com",
        subject="SendGrid debug",
        html_content="<p>debug</p>",
    )

    try:
        sg = SendGridAPIClient(key)
        resp = sg.send(msg)
        print("SendGrid response status:", getattr(resp, "status_code", None))
        print("SendGrid response body:", getattr(resp, "body", None))
        print("SendGrid response headers:", getattr(resp, "headers", None))
        return 0
    except HTTPError as e:
        print("HTTPError status:", getattr(e, "status_code", None))
        print("HTTPError body:", getattr(e, "body", None))
        print("HTTPError headers:", getattr(e, "headers", None))
        return 1
    except Exception as e:
        print("Unexpected exception:", repr(e))
        print(
            "Hint: si el error incluye SSLCertVerificationError/self-signed, "
            "define SSL_CERT_FILE en .env apuntando a un .pem con el certificado raíz de tu proxy/antivirus."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
