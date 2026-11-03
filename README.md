# StealthLedger
### Tamper-Evident Image Steganography & Secure Data Vault

StealthLedger is a Python project that embeds structured data inside supported image files using **Steghide**, then stores the resulting steganographic image in a **SQLite-backed, hash-linked ledger**. A salted scrypt passcode verifier is stored alongside each record to verify access before extraction.

> **Scope clarification:** This is a local, single-database, tamper-evident record chain. It is not a decentralized blockchain, distributed consensus network, or a replacement for a cryptographic key-management system.

## Core workflow

```text
Structured data
      |
      v
JSON serialization
      |
      v
Steghide + passphrase
      |
      v
Steganographic image bytes
      |
      +------> SHA-256 linked block
      |                |
      |                v
      |           SQLite ledger
      |
      v
Image returned to caller

Retrieval:
identifier -> scrypt passcode verification -> ledger payload
           -> Steghide extraction -> JSON decoding
```

## Features

- Hide JSON-compatible values or text inside JPEG/BMP images.
- Extract embedded payloads using a passphrase.
- Verify passphrases with bcrypt hashes.
- Persist records in SQLite.
- Maintain a per-ledger SHA-256 hash chain.
- Detect payload alteration and broken hash links.
- Use parameterized SQL statements.
- Avoid unsafe `pickle` deserialization.
- Run repeatable dataset benchmarks.
- Automated unit tests and GitHub Actions CI.

## Technology

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Image processing | Pillow |
| Steganography | Steghide command-line utility |
| Passcode hashing | Python scrypt (stdlib) |
| Ledger persistence | SQLite |
| Block integrity | SHA-256 |
| Serialization | JSON |
| Testing | unittest |
| CI | GitHub Actions |

## Repository layout

```text
StealthLedger-v1/
├── .github/workflows/python-ci.yml
├── tests/
│   ├── test_blockchain.py
│   └── test_stealthledger.py
├── test_dataset_3/
│   ├── data_to_hide/       # Demonstration payloads
│   ├── images/             # Cover images
│   └── passwords/          # DEMO ONLY; never use real passwords
├── blockchain.py
├── steganography.py
├── stealthledger.py
├── test2.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

1. Python 3.10 or newer.
2. Steghide installed and available on `PATH`.
3. JPEG or BMP cover images.
4. Windows, Linux, or macOS (Steghide installation differs by OS).

Check the executable:

```bash
steghide --version
```

Install Python dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Quick start

Use a cover image you own or are authorized to modify:

```bash
python stealthledger.py --image path/to/cover.jpg --identifier demo-001 --ledger my-ledger
```

The program asks for a passphrase without echoing it in the terminal. The output steganographic image is written to `stego-output/`, and ledger metadata is stored in `stealthledger.db`.

The Python API:

```python
from stealthledger import StealthLedger

ledger = StealthLedger("personal-vault", "jpg")

try:
    ledger.add_node(
        {"note": "Confidential demonstration", "version": 1},
        "cover.jpg",
        "record-001",
        "use-a-long-demo-passphrase",
    )

    recovered = ledger.retrieve_from_node(
        "record-001",
        "use-a-long-demo-passphrase",
    )
    print(recovered)
finally:
    ledger.close()
```

Payloads must be JSON-serializable. Supported examples include strings, numbers, lists, dictionaries, booleans, and `None`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The unit tests mock the external Steghide operation where appropriate. They test ledger persistence, tamper detection, passcode checks, and JSON serialization without requiring a real cover image.

## Run the dataset benchmark

The included dataset is a demonstration dataset. It contains sample passcodes and must never be used for real secrets.

```bash
python test2.py --dataset test_dataset_3 --ledger benchmark-run --format jpg --db benchmark.db
```

Results and generated images are written under:

```text
test_dataset_3/benchmark_output/
```

The benchmark checks that each retrieved payload matches its original text and reports average embedding and retrieval times.

## Database design

Records are stored in a single SQLite table, partitioned by `ledger_name`.

| Field | Purpose |
|---|---|
| ledger_name | Logical ledger identifier |
| block_index | Sequential index within a ledger |
| identifier | Unique record identifier within a ledger |
| payload | Steganographic image bytes |
| passcode_hash | bcrypt hash used for access verification |
| previous_hash | Hash of the preceding block |
| timestamp | Block creation time |
| block_hash | SHA-256 hash of canonical block metadata and payload digest |

The hash chain makes accidental or unauthorized payload changes detectable when the chain is verified. It does not prevent an attacker who can rewrite the entire database and recompute all hashes. Stronger tamper evidence requires an externally anchored signature or hash.

## Security notes and limitations

- **Never use `pickle.loads` on untrusted data.** This implementation uses JSON for payload serialization.
- Steghide receives the passphrase as a command-line argument. Depending on the operating system, process inspection may expose command arguments to other local users. Use this tool only in a trusted environment.
- scrypt protects the stored verifier; it does not replace Steghide encryption.
- The included benchmark password files are public demo fixtures. Do not reuse them.
- SQLite is local storage, not a distributed ledger.
- A local attacker with full database access may alter the database and recompute the chain. Consider externally signing or anchoring the latest block hash for stronger auditability.
- Back up the database securely. Protect the cover images and passphrases.
- Steganography does not guarantee that hidden content is undetectable.
- Do not embed credentials, payment secrets, or other high-impact data without a formal threat model and appropriate key management.

## Important compatibility note

This upgraded version uses a new SQLite schema in `stealthledger.db` and JSON payload serialization. It does not automatically migrate the original `database.db` records. Back up any existing database before upgrading. Legacy records serialized with pickle should only be migrated in an isolated, trusted environment after inspection.

## Roadmap

- [x] Replace pickle payload serialization with JSON.
- [x] Parameterize database queries and avoid dynamic table names.
- [x] Persist and verify a SHA-256 hash-linked record chain.
- [x] Add bcrypt passcode verification.
- [x] Add bounded Steghide subprocess execution and error handling.
- [x] Add repeatable benchmark runner.
- [x] Add automated unit tests and CI.
- [ ] Add a signed external chain checkpoint.
- [ ] Add encrypted database backup and restore.
- [ ] Add a desktop/web user interface.
- [ ] Add payload size and image-capacity preflight checks.
- [ ] Add structured logging and benchmark visualization.

## Contributing

1. Create a feature branch.
2. Keep changes focused.
3. Add or update tests.
4. Run `python -m unittest discover -s tests -v`.
5. Open a pull request with a clear description and test results.

## License

No license was supplied with the original archive. Add an appropriate license after confirming the project's ownership and distribution terms.

---

**StealthLedger** — Conceal data. Verify integrity. Retrieve securely.
