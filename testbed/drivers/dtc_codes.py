"""Named DTC codes for Task 1 stop-driving fault coverage.

Keep this aligned with common/Data/DTC.csv.
"""

from enum import IntEnum


class DtcSeverity(IntEnum):
    INVALID = 0
    FATAL = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4


class DtcCode(IntEnum):
    PRECHARGE_FAILED = 31
    DISCHARGE_FAILED = 32
    PDU_MAX_CURRENT_EXCEEDED = 69
    BMU_CLOSE_TO_EDGE = 71
    BOTS_FAILURE = 72
    EBOX_IL_FAILURE = 73
    BSPD_FAILURE = 74
    HVD_FAILURE = 75
    TSMS_FAILURE = 76
    HW_CHECK_FAILURE = 77
    CBRB_PRESSED = 78
    BATTERY_TASK_FAILURE = 79
    BMU_HV_FAULT = 80


# Mapping used by HIL coverage tests / operator checklist.
STOP_DRIVING_DTC_EXPECTATIONS = {
    "bots": {
        "code": DtcCode.BOTS_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Open BOTS / trip BOTS sense low",
    },
    "ebox": {
        "code": DtcCode.EBOX_IL_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Disconnect EBOX IL connector",
    },
    "bspd": {
        "code": DtcCode.BSPD_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Trip BSPD / open BSPD sense",
    },
    "hvd": {
        "code": DtcCode.HVD_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Remove HVD / open HVD sense",
    },
    "tsms": {
        "code": DtcCode.TSMS_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Turn TSMS off / open TSMS sense",
    },
    "hw_check": {
        "code": DtcCode.HW_CHECK_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Fail HW_CHECK contactor power sense",
    },
    "cbrb": {
        "code": DtcCode.CBRB_PRESSED,
        "severity": DtcSeverity.CRITICAL,
        "description": "Press cockpit BRB",
    },
    "precharge_fail": {
        "code": DtcCode.PRECHARGE_FAILED,
        "severity": DtcSeverity.FATAL,
        "description": "Force precharge step failure; check DTC_Data == PrechargeState",
    },
    "discharge_fail": {
        "code": DtcCode.DISCHARGE_FAILED,
        "severity": DtcSeverity.FATAL,
        "description": "Force discharge failure; check DTC_Data == DischargeState",
    },
    "battery_task_fail": {
        "code": DtcCode.BATTERY_TASK_FAILURE,
        "severity": DtcSeverity.FATAL,
        "description": "Force repeated battery-task failure until retry limit",
    },
    "close_to_edge": {
        "code": DtcCode.BMU_CLOSE_TO_EDGE,
        "severity": DtcSeverity.FATAL,
        "description": "Drive cell V/T near red limits until HV down",
    },
    "pdu_lv_overcurrent": {
        "code": DtcCode.PDU_MAX_CURRENT_EXCEEDED,
        "severity": DtcSeverity.ERROR,
        "description": "Force LV bus current above LV_MAX_CURRENT_AMPS",
    },
}
