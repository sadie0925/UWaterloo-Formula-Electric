#!/usr/bin/env python3
"""
Offline unit tests for DTC.csv coverage and DTC header generation.

Run from firmware repo root:
  python3 common/Scripts/test_dtc_generation.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DTC_CSV = REPO_ROOT / "common" / "Data" / "DTC.csv"
GENERATE_DTC = REPO_ROOT / "common" / "Scripts" / "generateDTC.py"

# Stop-driving / Task-1 DTCs we expect to exist after the coverage rewrite.
REQUIRED_DTCS = {
    31: {"NAME": "PrechargeFailed", "SEVERITY": "1", "DATA": "Step"},
    32: {"NAME": "DischargeFailed", "SEVERITY": "1", "DATA": "Step"},
    69: {"NAME": "PDU_Max_Current_Exceeded", "SEVERITY": "3", "DATA": "NA"},
    71: {"NAME": "BMU_Close_To_Edge", "SEVERITY": "1", "DATA": "NA"},
    72: {"NAME": "BOTS_Failure", "SEVERITY": "1", "DATA": "NA"},
    73: {"NAME": "EBOX_IL_Failure", "SEVERITY": "1", "DATA": "NA"},
    74: {"NAME": "BSPD_Failure", "SEVERITY": "1", "DATA": "NA"},
    75: {"NAME": "HVD_Failure", "SEVERITY": "1", "DATA": "NA"},
    76: {"NAME": "TSMS_Failure", "SEVERITY": "1", "DATA": "NA"},
    77: {"NAME": "HW_CHECK_Failure", "SEVERITY": "1", "DATA": "NA"},
    78: {"NAME": "CBRB_Pressed", "SEVERITY": "2", "DATA": "NA"},
    79: {"NAME": "Battery_Task_Failure", "SEVERITY": "1", "DATA": "FailureBit"},
    80: {"NAME": "BMU_HV_Fault", "SEVERITY": "1", "DATA": "Event"},
}

# Generic board errors should now carry a Line payload for root-cause tracing.
LINE_PAYLOAD_DTCS = {
    22: "PDU_ERROR",
    23: "VCU_F7_ERROR",
    24: "BMU_ERROR",
    25: "DCU_ERROR",
}


def load_dtc_rows():
    with DTC_CSV.open(newline="") as f:
        return {
            int(row["DTC CODE"]): row
            for row in csv.DictReader(f, skipinitialspace=True)
        }


class TestDtcCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_dtc_rows()

    def test_required_stop_driving_dtcs_exist(self):
        for code, expected in REQUIRED_DTCS.items():
            with self.subTest(code=code, name=expected["NAME"]):
                self.assertIn(code, self.rows, f"Missing DTC code {code}")
                row = self.rows[code]
                self.assertEqual(row["NAME"].strip(), expected["NAME"])
                self.assertEqual(row["SEVERITY"].strip(), expected["SEVERITY"])
                self.assertEqual(row["DATA"].strip(), expected["DATA"])

    def test_board_error_dtcs_carry_line_payload(self):
        for code, name in LINE_PAYLOAD_DTCS.items():
            with self.subTest(code=code, name=name):
                self.assertIn(code, self.rows)
                row = self.rows[code]
                self.assertEqual(row["NAME"].strip(), name)
                self.assertEqual(row["DATA"].strip(), "Line")

    def test_dtc_codes_are_unique(self):
        with DTC_CSV.open(newline="") as f:
            codes = [int(row["DTC CODE"]) for row in csv.DictReader(f, skipinitialspace=True)]
        self.assertEqual(len(codes), len(set(codes)))

    def test_generate_dtc_creates_expected_bmu_macros(self):
        with tempfile.TemporaryDirectory() as tmp:
            # generateDTC.py writes relative to CWD under Gen/<target>/Inc
            env = os.environ.copy()
            proc = subprocess.run(
                [sys.executable, str(GENERATE_DTC), "bmu"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

            header = REPO_ROOT / "Gen" / "bmu" / "Inc" / "bmu_dtc.h"
            self.assertTrue(header.exists(), f"Missing generated header {header}")
            text = header.read_text()

            expected_macros = [
                "#define sendDTC_FATAL_BOTS_Failure() sendDTCMessage(72, 1, 0)",
                "#define sendDTC_FATAL_EBOX_IL_Failure() sendDTCMessage(73, 1, 0)",
                "#define sendDTC_FATAL_BSPD_Failure() sendDTCMessage(74, 1, 0)",
                "#define sendDTC_FATAL_HVD_Failure() sendDTCMessage(75, 1, 0)",
                "#define sendDTC_FATAL_TSMS_Failure() sendDTCMessage(76, 1, 0)",
                "#define sendDTC_FATAL_HW_CHECK_Failure() sendDTCMessage(77, 1, 0)",
                "#define sendDTC_CRITICAL_CBRB_Pressed() sendDTCMessage(78, 2, 0)",
                "#define sendDTC_FATAL_Battery_Task_Failure(FailureBit) sendDTCMessage(79, 1, FailureBit)",
                "#define sendDTC_FATAL_BMU_HV_Fault(Event) sendDTCMessage(80, 1, Event)",
                "#define sendDTC_FATAL_BMU_ERROR(Line) sendDTCMessage(24, 1, Line)",
                "#define sendDTC_FATAL_PrechargeFailed(Step) sendDTCMessage(31, 1, Step)",
                "#define sendDTC_FATAL_DischargeFailed(Step) sendDTCMessage(32, 1, Step)",
            ]
            for macro in expected_macros:
                with self.subTest(macro=macro):
                    self.assertIn(macro, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
