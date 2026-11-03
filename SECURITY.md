# Security Policy

## Reporting a vulnerability

Do not publish exploitable details or real secrets in an issue. Contact the repository maintainer privately through GitHub.

## Security boundaries

StealthLedger is a research/demo project and has not undergone an independent security audit.

Known limitations:
- Steghide passphrases are passed as process arguments by the current CLI integration.
- SQLite hash chains are tamper-evident, not tamper-proof against an attacker who can rewrite the full database.
- Demo dataset password files are intentionally included for reproducible testing and are not secrets.
- The application does not provide a complete key-management or secure deletion system.

Do not use this project to store production credentials, financial secrets, or regulated data without a formal security review.
