# SPDX-License-Identifier: MIT
import tempfile
import unittest
from pathlib import Path

from fossils.fossil_record_export import build_dataset, canonical_architecture, generate_sample_history, load_sqlite_history


class TestFossilRecordExport(unittest.TestCase):
    def test_canonical_architecture(self):
        self.assertEqual(canonical_architecture("power8", "IBM POWER8 S824", "POWER"), "power8")
        self.assertEqual(canonical_architecture("modern", "x86-64 (Modern)", "x86"), "modern_x86")
        self.assertEqual(canonical_architecture("aarch64", "Apple Silicon", "ARM"), "apple_silicon")
        self.assertEqual(canonical_architecture("mips64", "Unknown", "MIPS"), "mips")

    def test_generate_sample_history(self):
        miners = [{"miner": "RTCabc", "device_arch": "power8", "hardware_type": "POWER8", "device_family": "POWER", "antiquity_multiplier": 2.0, "entropy_score": 0.7, "last_attest": 1774720000}]
        records = generate_sample_history(miners, current_epoch=115, sample_epochs=12)
        self.assertTrue(records)
        self.assertTrue(all(record.epoch >= 104 for record in records))
        self.assertTrue(all(record.architecture == "power8" for record in records))

    def test_build_dataset(self):
        miners = [{"miner": "RTCxyz", "device_arch": "modern", "hardware_type": "x86-64 (Modern)", "device_family": "x86", "antiquity_multiplier": 1.0, "entropy_score": 0.2, "last_attest": 1774720000}]
        dataset = build_dataset(generate_sample_history(miners, 115, 8), 115, "test")
        self.assertEqual(dataset["current_epoch"], 115)
        self.assertIn("records", dataset)
        self.assertIn("summary", dataset)

    def test_load_sqlite_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "fossils.db"
            import sqlite3

            conn = sqlite3.connect(db_path)
            conn.execute(
                """
                CREATE TABLE attestation_history (
                    epoch INTEGER,
                    miner_id TEXT,
                    device_arch TEXT,
                    hardware_type TEXT,
                    device_family TEXT,
                    rtc_earned REAL,
                    fingerprint_quality REAL,
                    antiquity_multiplier REAL,
                    attested_at INTEGER
                )
                """
            )
            conn.execute("INSERT INTO attestation_history VALUES (42, 'RTC123', 'power8', 'IBM POWER8 S824', 'POWER', 1.2, 0.88, 2.0, 1774720000)")
            conn.commit()
            conn.close()

            records = load_sqlite_history(db_path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].architecture, "power8")
            self.assertEqual(records[0].epoch, 42)


if __name__ == "__main__":
    unittest.main()
