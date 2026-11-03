import tempfile
import unittest
from pathlib import Path

from blockchain import Blockchain


class BlockchainTests(unittest.TestCase):
    def test_add_and_reload_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "test.db"
            ledger = Blockchain("unit-test", db)
            ledger.add_block(b"payload-one", "record-one", b"bcrypt-hash")
            self.assertTrue(ledger.is_chain_valid())
            self.assertEqual(len(ledger.chain), 1)
            ledger.close()

            reopened = Blockchain("unit-test", db)
            self.assertEqual(reopened.chain[0].data, b"payload-one")
            self.assertTrue(reopened.is_chain_valid())
            reopened.close()

    def test_duplicate_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Blockchain("unit-test", Path(directory) / "test.db")
            ledger.add_block(b"one", "same-id", b"hash")
            with self.assertRaises(Exception):
                ledger.add_block(b"two", "same-id", b"hash")
            ledger.close()

    def test_tampered_payload_invalidates_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "test.db"
            ledger = Blockchain("unit-test", db)
            ledger.add_block(b"original", "record", b"hash")
            ledger.conn.execute(
                "UPDATE ledger_blocks SET payload = ? WHERE ledger_name = ?",
                (b"tampered", "unit-test"),
            )
            self.assertFalse(ledger.is_chain_valid())
            ledger.close()


if __name__ == "__main__":
    unittest.main()
