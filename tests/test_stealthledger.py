import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from stealthledger import StealthLedger


class FakeSteganography:
    payload = b""

    def __init__(self, file_format):
        pass

    def hide_data_in_image(self, data, image, passcode):
        FakeSteganography.payload = data
        return image

    def extract_data_from_image(self, image, passcode):
        return FakeSteganography.payload


def make_jpeg(path):
    image = Image.new("RGB", (8, 8), color="white")
    image.save(path, format="JPEG")


class StealthLedgerTests(unittest.TestCase):
    @patch("stealthledger.SteganographyTool", FakeSteganography)
    def test_json_payload_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "cover.jpg"
            make_jpeg(image)
            ledger = StealthLedger("test", "jpg", Path(directory) / "db.sqlite")
            try:
                ledger.add_node(
                    {"message": "hello", "amount": 12.5},
                    image, "record-1", "strong-demo-passphrase",
                )
                result = ledger.retrieve_from_node("record-1", "strong-demo-passphrase")
                self.assertEqual(result, {"message": "hello", "amount": 12.5})
            finally:
                ledger.close()

    @patch("stealthledger.SteganographyTool", FakeSteganography)
    def test_wrong_passphrase_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "cover.jpg"
            make_jpeg(image)
            ledger = StealthLedger("test", "jpg", Path(directory) / "db.sqlite")
            try:
                ledger.add_node("secret", image, "record-1", "correct-passphrase")
                with self.assertRaises(PermissionError):
                    ledger.retrieve_from_node("record-1", "incorrect-passphrase")
            finally:
                ledger.close()

    def test_non_json_payload_is_rejected(self):
        with self.assertRaises(ValueError):
            StealthLedger._serialize_payload(object())


if __name__ == "__main__":
    unittest.main()
