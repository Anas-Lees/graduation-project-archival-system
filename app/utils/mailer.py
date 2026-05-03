from datetime import datetime
from flask import current_app


def send_email(to: str, subject: str, body: str) -> None:
    """FR15: Notification stub. Logs email to instance/email.log instead of SMTP."""
    line = (
        f"[{datetime.utcnow().isoformat()}Z] TO={to} | SUBJECT={subject}\n"
        f"  {body}\n{'-' * 60}\n"
    )
    path = current_app.config["EMAIL_LOG_PATH"]
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as e:
        current_app.logger.error("email log failed: %s", e)
