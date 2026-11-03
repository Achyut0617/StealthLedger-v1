"""Steghide integration with safe temporary-file handling.

Requires the external `steghide` executable to be installed separately.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError


class SteganographyError(RuntimeError):
    """Raised when image embedding or extraction fails."""


class SteganographyTool:
    SUPPORTED_FORMATS = {"jpg", "jpeg", "bmp"}

    def __init__(self, file_format: str, timeout: int = 120):
        normalized = file_format.lower().lstrip(".")
        if normalized not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {file_format}")
        if shutil.which("steghide") is None:
            raise RuntimeError(
                "steghide executable was not found. Install Steghide and add it to PATH."
            )
        self.file_format = normalized
        self.timeout = timeout

    @staticmethod
    def is_supported_format(file_format: str) -> bool:
        return file_format.lower().lstrip(".") in SteganographyTool.SUPPORTED_FORMATS

    @staticmethod
    def _validate_passphrase(passphrase: str) -> None:
        if not isinstance(passphrase, str) or not passphrase:
            raise ValueError("Passphrase must be a non-empty string")
        if "\x00" in passphrase:
            raise ValueError("Passphrase contains an invalid null character")

    def hide_data_in_image(
        self, data: bytes, input_image_data: bytes, passcode: str
    ) -> bytes:
        self._validate_passphrase(passcode)
        if not isinstance(data, (bytes, bytearray)) or not data:
            raise ValueError("Hidden payload must be non-empty bytes")
        if not isinstance(input_image_data, (bytes, bytearray)):
            raise TypeError("Image input must be bytes")

        try:
            with Image.open(BytesIO(input_image_data)) as image:
                image.verify()
            with Image.open(BytesIO(input_image_data)) as image:
                image_format = (image.format or "").lower()
                if image_format not in {"jpeg", "bmp"}:
                    raise ValueError("Input image must be JPEG or BMP")
                suffix = "jpg" if image_format == "jpeg" else "bmp"
                image_bytes = bytes(input_image_data)
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Input is not a valid supported image") from exc

        with tempfile.TemporaryDirectory(prefix="stealthledger-") as temp_dir:
            input_path = Path(temp_dir) / f"cover.{suffix}"
            output_path = Path(temp_dir) / f"stego.{suffix}"
            payload_path = Path(temp_dir) / "payload.bin"
            input_path.write_bytes(image_bytes)
            payload_path.write_bytes(bytes(data))

            command = [
                "steghide", "embed", "-cf", str(input_path),
                "-ef", str(payload_path), "-sf", str(output_path),
                "-p", passcode, "-f",
            ]
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True,
                    timeout=self.timeout, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise SteganographyError("Steghide embedding timed out") from exc

            if result.returncode != 0 or not output_path.is_file():
                detail = (result.stderr or result.stdout or "Unknown Steghide error").strip()
                raise SteganographyError(f"Steghide embedding failed: {detail}")
            return output_path.read_bytes()

    def extract_data_from_image(self, steg_image_data: bytes, passcode: str) -> bytes:
        self._validate_passphrase(passcode)
        if not isinstance(steg_image_data, (bytes, bytearray)):
            raise TypeError("Steganographic image must be bytes")

        with tempfile.TemporaryDirectory(prefix="stealthledger-") as temp_dir:
            image_path = Path(temp_dir) / f"stego.{self.file_format}"
            output_path = Path(temp_dir) / "payload.bin"
            image_path.write_bytes(bytes(steg_image_data))

            command = [
                "steghide", "extract", "-sf", str(image_path),
                "-xf", str(output_path), "-p", passcode, "-f",
            ]
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True,
                    timeout=self.timeout, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise SteganographyError("Steghide extraction timed out") from exc

            if result.returncode != 0 or not output_path.is_file():
                detail = (result.stderr or result.stdout or "Wrong passphrase or invalid image").strip()
                raise SteganographyError(f"Steghide extraction failed: {detail}")
            return output_path.read_bytes()
