"""SQLite-backed, tamper-evident ledger storage.

This is a local append-only record chain, not a decentralized blockchain.
No pickle serialization is used.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Block:
    index: int
    data: bytes
    previous_hash: str
    timestamp: float
    hash: str

    @staticmethod
    def calculate_hash_for(
        index: int, data: bytes, previous_hash: str, timestamp: float
    ) -> str:
        payload_hash = hashlib.sha256(data).hexdigest()
        canonical = json.dumps(
            {
                "index": index,
                "payload_sha256": payload_hash,
                "previous_hash": previous_hash,
                "timestamp": timestamp,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @classmethod
    def create(
        cls, index: int, data: bytes, previous_hash: str, timestamp: Optional[float] = None
    ) -> "Block":
        created_at = time.time() if timestamp is None else float(timestamp)
        digest = cls.calculate_hash_for(index, data, previous_hash, created_at)
        return cls(index, data, previous_hash, created_at, digest)

    def calculate_hash(self) -> str:
        return self.calculate_hash_for(
            self.index, self.data, self.previous_hash, self.timestamp
        )


class Blockchain:
    """A per-ledger chain persisted in one SQLite database."""

    def __init__(self, name: str, db_path: str | Path = "stealthledger.db"):
        if not name or not name.strip():
            raise ValueError("Ledger name is required")
        self.name = name.strip()
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(
            self.db_path, timeout=30, isolation_level=None, check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 30000")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.create_table()
        self.chain = self.load_chain_from_db()

    def create_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_name TEXT NOT NULL,
                block_index INTEGER NOT NULL,
                identifier TEXT NOT NULL,
                payload BLOB NOT NULL,
                passcode_hash BLOB NOT NULL,
                previous_hash TEXT NOT NULL,
                timestamp REAL NOT NULL,
                block_hash TEXT NOT NULL,
                UNIQUE (ledger_name, identifier),
                UNIQUE (ledger_name, block_index)
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ledger_identifier "
            "ON ledger_blocks(ledger_name, identifier)"
        )

    @staticmethod
    def _row_to_block(row: sqlite3.Row) -> Block:
        return Block(
            index=row["block_index"],
            data=bytes(row["payload"]),
            previous_hash=row["previous_hash"],
            timestamp=row["timestamp"],
            hash=row["block_hash"],
        )

    def load_chain_from_db(self) -> list[Block]:
        rows = self.conn.execute(
            "SELECT * FROM ledger_blocks WHERE ledger_name = ? ORDER BY block_index",
            (self.name,),
        ).fetchall()
        return [self._row_to_block(row) for row in rows]

    def get_latest_block(self) -> Optional[Block]:
        if not self.chain:
            return None
        return self.chain[-1]

    def add_block(self, data: bytes, identifier: str, passcode_hash: bytes) -> Block:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Block payload must be bytes")
        if not identifier or not identifier.strip():
            raise ValueError("Identifier is required")
        if not isinstance(passcode_hash, (bytes, bytearray)) or not passcode_hash:
            raise ValueError("A passcode hash is required")

        payload = bytes(data)
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            latest = self.conn.execute(
                "SELECT block_index, block_hash FROM ledger_blocks "
                "WHERE ledger_name = ? ORDER BY block_index DESC LIMIT 1",
                (self.name,),
            ).fetchone()

            index = 0 if latest is None else latest["block_index"] + 1
            previous_hash = "0" if latest is None else latest["block_hash"]
            block = Block.create(index, payload, previous_hash)

            self.conn.execute(
                """
                INSERT INTO ledger_blocks
                (ledger_name, block_index, identifier, payload, passcode_hash,
                 previous_hash, timestamp, block_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.name, block.index, identifier.strip(), payload,
                    bytes(passcode_hash), block.previous_hash,
                    block.timestamp, block.hash,
                ),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

        self.chain = self.load_chain_from_db()
        return block

    def get_record(self, identifier: str):
        return self.conn.execute(
            "SELECT * FROM ledger_blocks WHERE ledger_name = ? AND identifier = ?",
            (self.name, identifier),
        ).fetchone()

    def get_block_by_identifier(self, identifier: str) -> Optional[Block]:
        row = self.get_record(identifier)
        return None if row is None else self._row_to_block(row)

    def is_chain_valid(self) -> bool:
        blocks = self.load_chain_from_db()
        expected_previous = "0"

        for expected_index, block in enumerate(blocks):
            if block.index != expected_index:
                return False
            if block.previous_hash != expected_previous:
                return False
            if block.hash != block.calculate_hash():
                return False
            expected_previous = block.hash

        self.chain = blocks
        return True

    def display_chain(self) -> None:
        for block in self.load_chain_from_db():
            print(
                f"Block {block.index}: payload_sha256="
                f"{hashlib.sha256(block.data).hexdigest()}, "
                f"hash={block.hash}, previous={block.previous_hash}"
            )

    def close(self) -> None:
        self.conn.close()


def create_blockchain(name: str, db_path: str | Path = "stealthledger.db") -> Blockchain:
    ledger = Blockchain(name, db_path)
    if not ledger.chain:
        # Genesis payload is deterministic and contains no user secret.
        ledger.add_block(b"STEALTHLEDGER_GENESIS", "0th-block", b"genesis")
    return ledger
