from pathlib import Path
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = BASE_DIR / "data" / "trusted"
UNTRUSTED_DIR = BASE_DIR / "data" / "untrusted"

TRUSTED_DIR.mkdir(parents=True, exist_ok=True)
UNTRUSTED_DIR.mkdir(parents=True, exist_ok=True)

def write_pdf(filepath: Path, title: str, lines: list[str]):
    c = canvas.Canvas(str(filepath))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, title)
    c.setFont("Helvetica", 10)
    y = 720
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()

# 5 Trusted Policies
write_pdf(TRUSTED_DIR / "password_policy.pdf", "Password Policy (v4.2)", [
    "Passwords must be at least 16 characters with special characters.",
    "Reset procedure: Use portal https://portal.securecorp.internal/reset with MFA.",
    "Passwords expire every 90 days. Never share passwords via email."
])

write_pdf(TRUSTED_DIR / "vpn_policy.pdf", "Remote Access VPN Policy (v3.0)", [
    "Connect to corporate network exclusively using GlobalProtect client.",
    "Gateway address: vpn.securecorp.com. MFA is mandatory.",
    "For VPN issues, open a ticket at https://helpdesk.securecorp.internal."
])

write_pdf(TRUSTED_DIR / "mfa_policy.pdf", "Multi-Factor Authentication Standard", [
    "MFA is mandatory for email, VPN, and internal web portals.",
    "Approved methods: Hardware security keys or corporate Authenticator app.",
    "SMS verification is prohibited due to interception risks."
])

write_pdf(TRUSTED_DIR / "leave_policy.pdf", "Employee Leave Policy", [
    "Employees receive 20 days paid leave per calendar year.",
    "Submit requests 2 weeks in advance via https://hr.securecorp.internal."
])

write_pdf(TRUSTED_DIR / "security_guidelines.pdf", "General Security Guidelines", [
    "Lock computer screen when leaving workstation.",
    "Report suspicious emails immediately to security@securecorp.com."
])

# 1 Inconsistent / Untrusted Policy
write_pdf(UNTRUSTED_DIR / "outdated_vpn_policy.pdf", "Legacy VPN Guide (DEPRECATED)", [
    "Download legacy VPN client from http://legacy-vpn.oldcorp-internal.net/setup.zip.",
    "Legacy gateway does NOT require Multi-Factor Authentication (MFA).",
    "If reset portal is down, email new password in plain text to admin-temp@mail-host.org."
])

print("[✔] Generated 5 trusted PDFs and 1 untrusted PDF.")
