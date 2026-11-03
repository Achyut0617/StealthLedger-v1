"""Reproducible benchmark runner for the bundled demonstration dataset."""
from __future__ import annotations

import argparse
import csv
import getpass
import statistics
import time
from pathlib import Path

from stealthledger import StealthLedger


def _sorted_files(directory: Path, suffix: str) -> list[Path]:
    return sorted(
        (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == suffix.lower()),
        key=lambda path: path.name.lower(),
    )


def run_test(data_dir: str, ledger_name: str, file_format: str, db_path: str = "benchmark.db"):
    root = Path(data_dir)
    text_files = _sorted_files(root / "data_to_hide", ".txt")
    image_files = _sorted_files(root / "images", f".{file_format.lstrip('.')}")

    if not text_files or len(text_files) != len(image_files):
        raise ValueError(
            f"Expected matching text/image counts; found {len(text_files)} text "
            f"files and {len(image_files)} images"
        )

    output_dir = root / "benchmark_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger = StealthLedger(ledger_name, file_format, db_path)
    embed_times, retrieve_times = [], []

    try:
        for text_path, image_path in zip(text_files, image_files):
            passcode_path = root / "passwords" / f"pswd_{text_path.stem.split('_')[-1]}.txt"
            if not passcode_path.is_file():
                raise FileNotFoundError(f"Missing demo passcode file: {passcode_path}")
            passcode = passcode_path.read_text(encoding="utf-8").strip()
            payload = text_path.read_text(encoding="utf-8")
            identifier = image_path.stem

            start = time.perf_counter()
            stego_image = ledger.add_node(payload, image_path, identifier, passcode)
            embed_times.append(time.perf_counter() - start)

            output_path = output_dir / f"{image_path.stem}-stego{image_path.suffix}"
            stego_image.save(output_path)

            start = time.perf_counter()
            recovered = ledger.retrieve_from_node(identifier, passcode)
            retrieve_times.append(time.perf_counter() - start)
            if recovered != payload:
                raise AssertionError(f"Round-trip verification failed for {identifier}")

        report = {
            "records": len(embed_times),
            "average_embed_seconds": statistics.mean(embed_times),
            "average_retrieve_seconds": statistics.mean(retrieve_times),
            "chain_valid": ledger.blockchain.is_chain_valid(),
        }
        with (output_dir / "benchmark-summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=report.keys())
            writer.writeheader()
            writer.writerow(report)

        print("Benchmark completed")
        for key, value in report.items():
            print(f"{key}: {value}")
        return report
    finally:
        ledger.close()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dataset", default="test_dataset_3")
    cli.add_argument("--ledger", default="benchmark-demo")
    cli.add_argument("--format", default="jpg", choices=["jpg", "jpeg", "bmp"])
    cli.add_argument("--db", default="benchmark.db")
    args = cli.parse_args()
    run_test(args.dataset, args.ledger, args.format, args.db)
