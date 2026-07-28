from typing import Dict, List
from datetime import datetime


class DTC:
    def __init__(self, code: int, severity: int, data: int, time: datetime):
        self.code = code
        self.data = data
        self.severity = severity
        self.was_read = False
        self.time_logged = time

    def read(self):
        self.was_read = True
        return self.data


class DTCLogger:
    def __init__(self, can_db):
        self.dtc_log: Dict[int, List[DTC]] = {}  # {code : List of DTC objects}
        self.db = can_db

    def log_dtc(self, msg):
        decoded_dtc = self.db.decode_message(
            msg.arbitration_id,
            msg.data,
            allow_truncated=True,
            decode_choices=False,
            decode_containers=False
        )

        code = decoded_dtc['DTC_CODE']
        severity = decoded_dtc['DTC_Severity']
        data = decoded_dtc['DTC_Data']

        received_dtc = DTC(code=code, severity=severity,
                           data=data, time=datetime.now())

        if code not in self.dtc_log:
            self.dtc_log[code] = []

        self.dtc_log[code].append(received_dtc)

    def get_dtc_structs(self, code: int) -> bool:
        assert self.has_dtc(code), f"DTC Code {code} not found in DTC Log"

        # Given a DTC Code, return a list of unread DTC objects themselves
        dtcs = []
        for dtc in reversed(self.dtc_log[code]):
            if not dtc.was_read:
                dtcs.append(dtc)
                dtc.read()
        return dtcs

    def get_dtc_data(self, code: int) -> List[int]:
        assert self.has_dtc(code), f"DTC Code {code} not found in DTC Log"

        # Given a DTC Code, return a list of DTC data received with that code
        dtcs_data = []
        for dtc in reversed(self.dtc_log[code]):
            if not dtc.was_read:
                dtcs_data.append(dtc.read())
        return dtcs_data

    def has_dtc(self, code: int) -> bool:
        # Check if a DTC code was logged
        return code in self.dtc_log

    def list_dtcs(self) -> List[int]:
        # Return a list of all DTC codes that were logged
        # Note: does not provide any info on how many times they were logged
        return list(self.dtc_log.keys())

    def reset_logger(self) -> None:
        # Clear all DTCs from the log
        self.dtc_log = {}

    def expect_dtc(self, code: int, severity: int = None, data: int = None) -> bool:
        """
        Assert-style helper for HIL tests.

        Returns True if an unread DTC matching code (and optional severity/data)
        was found. Marks matching unread DTCs as read.
        """
        assert self.has_dtc(code), f"DTC Code {code} not found in DTC Log"

        matches = []
        for dtc in reversed(self.dtc_log[code]):
            if dtc.was_read:
                continue
            if severity is not None and dtc.severity != severity:
                continue
            if data is not None and dtc.data != data:
                continue
            matches.append(dtc)

        assert matches, (
            f"No unread DTC match for code={code}, severity={severity}, data={data}. "
            f"Logged={[(d.severity, d.data, d.was_read) for d in self.dtc_log.get(code, [])]}"
        )

        for dtc in matches:
            dtc.read()
        return True

    def wait_for_dtc(self, code: int, timeout_s: float = 5.0, poll_s: float = 0.1,
                     severity: int = None, data: int = None) -> bool:
        """Poll until an unread matching DTC appears or timeout expires."""
        import time

        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if self.has_dtc(code):
                try:
                    return self.expect_dtc(code, severity=severity, data=data)
                except AssertionError:
                    pass
            time.sleep(poll_s)

        raise AssertionError(
            f"Timed out after {timeout_s}s waiting for DTC code={code} "
            f"severity={severity} data={data}. Seen codes={self.list_dtcs()}"
        )
