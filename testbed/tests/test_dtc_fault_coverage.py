"""
HIL-oriented DTC coverage hooks for Task 1 stop-driving faults.

These tests do NOT invent fake CAN traffic. They use the existing DTCLogger on
the vehicle bus and assert that expected DTC codes arrive after an operator /
HIL setup injects each fault.

Offline (no hardware):
  python3 common/Scripts/test_dtc_generation.py

HIL (with Vector/socketCAN + flashed boards):
  cd testbed
  slash run tests/test_dtc_fault_coverage.py -k test_dtc_code_table_is_complete
  slash run tests/test_dtc_fault_coverage.py -k test_wait_for_injected_fault_dtc
"""

from __future__ import annotations

import slash
from drivers.dtc_codes import (
    DtcCode,
    STOP_DRIVING_DTC_EXPECTATIONS,
)
from testbeds.hil_testbed import teststand


def _bmu(teststand):
    return teststand.vehicle_boards["bmu"]


def _logger(teststand):
    return _bmu(teststand).dtc_logger


def _g_get(name, default):
    return getattr(slash.g, name, default)


def test_dtc_code_table_is_complete():
    """Sanity check that HIL constants stay aligned with Task 1 coverage."""
    expected_codes = {
        DtcCode.BOTS_FAILURE,
        DtcCode.EBOX_IL_FAILURE,
        DtcCode.BSPD_FAILURE,
        DtcCode.HVD_FAILURE,
        DtcCode.TSMS_FAILURE,
        DtcCode.HW_CHECK_FAILURE,
        DtcCode.CBRB_PRESSED,
        DtcCode.PRECHARGE_FAILED,
        DtcCode.DISCHARGE_FAILED,
        DtcCode.BATTERY_TASK_FAILURE,
        DtcCode.BMU_CLOSE_TO_EDGE,
        DtcCode.PDU_MAX_CURRENT_EXCEEDED,
    }
    table_codes = {item["code"] for item in STOP_DRIVING_DTC_EXPECTATIONS.values()}
    assert expected_codes == table_codes


@slash.parametrize(("fault_name",), [(name,) for name in STOP_DRIVING_DTC_EXPECTATIONS.keys()])
def test_print_fault_injection_checklist(fault_name):
    """
    Prints the operator checklist for each covered fault.

    This always passes and is useful during bring-up to confirm which DTC
    should appear for each injected fault.
    """
    item = STOP_DRIVING_DTC_EXPECTATIONS[fault_name]
    slash.logger.info(
        f"[DTC checklist] fault={fault_name} "
        f"code={int(item['code'])} severity={int(item['severity'])} "
        f"how={item['description']}"
    )


@slash.parametrize(("fault_name",), [(name,) for name in STOP_DRIVING_DTC_EXPECTATIONS.keys()])
def test_wait_for_injected_fault_dtc(fault_name, teststand):
    """
    Hardware/HIL test hook.

    Procedure:
      1. Flash updated BMU/PDU firmware.
      2. Start this test for one fault at a time.
      3. Within the wait window, inject the fault described in the checklist.
      4. The test passes when the matching DTC is observed on the vehicle CAN bus.

    Skip this test in CI / no-hardware environments:
      slash run tests/test_dtc_fault_coverage.py -k test_dtc_code_table_is_complete
    """
    if _g_get("skip_hardware_dtc_injection", False):
        slash.skip_test("skip_hardware_dtc_injection=True")

    item = STOP_DRIVING_DTC_EXPECTATIONS[fault_name]
    logger = _logger(teststand)
    logger.reset_logger()

    slash.logger.info(
        f"Inject fault now: {fault_name} -> expect DTC {int(item['code'])}. "
        f"{item['description']}"
    )

    # Give the operator time to inject; increase if needed for manual testing.
    timeout_s = _g_get("dtc_injection_timeout_s", 20.0)
    logger.wait_for_dtc(
        code=int(item["code"]),
        timeout_s=timeout_s,
        severity=int(item["severity"]),
    )


def test_helper_expect_dtc_rejects_missing(teststand):
    """
    Lightweight logger helper check.

    Validates that expect_dtc fails cleanly when no matching DTC has been
    received yet. Requires an initialized vehicle DTC logger fixture.
    """
    logger = _logger(teststand)
    logger.reset_logger()
    try:
        logger.expect_dtc(DtcCode.BOTS_FAILURE)
        raise AssertionError("expect_dtc should fail when logger is empty")
    except AssertionError as exc:
        assert "not found" in str(exc).lower() or "no unread" in str(exc).lower()
