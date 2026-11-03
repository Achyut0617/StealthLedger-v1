"""Public API for storing and retrieving JSON-compatible data in images."""
from __future__ import annotations

import json
import hashlib
import hmac
import secrets
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

from blockchain import create_blockchain
from steganography import SteganographyTool


class StealthLedger:
    def __init__(
        self, name: str, file_format: str, db_path: str | Path = "stealthledger.db"
    ) -> None:
        self.name = name
        self.file_format = file_format
        self.steganography = SteganographyTool(file_format=file_format)
        self.blockchain = create_blockchain(name, db_path)

    @staticmethod
    def _hash_passcode(passcode: str) -> bytes:
        if not isinstance(passcode, str) or len(passcode) < 8:
            raise ValueError("Passcode must contain at least 8 characters")
        salt = secrets.token_bytes(16)
        derived = hashlib.scrypt(
            passcode.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
        )
        return b"scrypt$16384$8$1$" + salt.hex().encode("ascii") + b"$" + derived.hex().encode("ascii")

    @staticmethod
    def _verify_passcode(passcode: str, stored: bytes) -> bool:
        try:
            algorithm, n, r, p, salt_hex, digest_hex = stored.decode("ascii").split("$")
            if algorithm != "scrypt":
                return False
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.scrypt(
                passcode.encode("utf-8"),
                salt=bytes.fromhex(salt_hex),
                n=int(n), r=int(r), p=int(p), dklen=len(expected),
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError, UnicodeDecodeError):
            return False

    @staticmethod
    def _serialize_payload(data: Any) -> bytes:
        try:
            return json.dumps(
                data, ensure_ascii=False, separators=(",", ":"), allow_nan=False
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("Data must be JSON-serializable") from exc

    @staticmethod
    def _deserialize_payload(payload: bytes) -> Any:
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Embedded payload is not valid StealthLedger JSON data") from exc

    def add_node(self, data: Any, image: str | Path, identifier: str, passcode: str):
        image_path = Path(image)
        if not image_path.is_file():
            raise FileNotFoundError(f"Cover image not found: {image_path}")
        if not identifier or not identifier.strip():
            raise ValueError("Identifier is required")

        original_image = image_path.read_bytes()
        payload = self._serialize_payload(data)
        stego_image = self.steganography.hide_data_in_image(
            payload, original_image, passcode
        )
        passcode_hash = self._hash_passcode(passcode)

        # Persist only after successful embedding.
        self.blockchain.add_block(stego_image, identifier, passcode_hash)
        return Image.open(BytesIO(stego_image)).copy()

    def retrieve_from_node(self, identifier: str, passcode: str):
        record = self.blockchain.get_record(identifier)
        if record is None:
            raise KeyError(f"No node found for identifier: {identifier}")

        if not self._verify_passcode(passcode, bytes(record["passcode_hash"])):
            raise PermissionError("Passcode does not match")

        block = self.blockchain.get_block_by_identifier(identifier)
        if block is None:
            raise RuntimeError("Ledger record disappeared during retrieval")

        payload = self.steganography.extract_data_from_image(block.data, passcode)
        return self._deserialize_payload(payload)

    # Backwards-compatible spelling used by the original project.
    def retrive_from_node(self, identifier: str, passcode: str):
        return self.retrieve_from_node(identifier, passcode)

    def close(self) -> None:
        self.blockchain.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="StealthLedger image data vault demo")
    parser.add_argument("--image", required=True, help="JPEG/BMP cover image")
    parser.add_argument("--identifier", default="demo-record")
    parser.add_argument("--ledger", default="demo-ledger")
    parser.add_argument("--db", default="stealthledger.db")
    args = parser.parse_args()

    import getpass
    secret = getpass.getpass("Passphrase (minimum 8 characters): ")
    ledger = StealthLedger(args.ledger, Path(args.image).suffix, args.db)
    try:
        result = ledger.add_node(
            {"message": "StealthLedger demo payload"}, args.image,
            args.identifier, secret,
        )
        output = Path("stego-output") / f"{Path(args.image).stem}-stego{Path(args.image).suffix}"
        output.parent.mkdir(exist_ok=True)
        result.save(output)
        print(f"Embedded image written to: {output}")
    finally:
        ledger.close()
