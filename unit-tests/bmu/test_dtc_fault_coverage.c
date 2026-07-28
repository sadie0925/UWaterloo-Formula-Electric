/**
 * @file test_dtc_fault_coverage.c
 * @brief Unit tests for stop-driving DTC codes and send macros.
 *
 * Validates that DTC.csv-generated enums/macros for Task 1 fault coverage
 * map to the expected CAN DTC codes and call sendDTCMessage with the right
 * code, severity, and data payload.
 */
#include "unity.h"

#include "bmu_dtc.h"
#include "Mock_userCan.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_stop_driving_dtc_enum_codes(void)
{
    TEST_ASSERT_EQUAL_INT(31, FATAL_PrechargeFailed);
    TEST_ASSERT_EQUAL_INT(32, FATAL_DischargeFailed);
    TEST_ASSERT_EQUAL_INT(69, ERROR_PDU_Max_Current_Exceeded);
    TEST_ASSERT_EQUAL_INT(71, FATAL_BMU_Close_To_Edge);
    TEST_ASSERT_EQUAL_INT(72, FATAL_BOTS_Failure);
    TEST_ASSERT_EQUAL_INT(73, FATAL_EBOX_IL_Failure);
    TEST_ASSERT_EQUAL_INT(74, FATAL_BSPD_Failure);
    TEST_ASSERT_EQUAL_INT(75, FATAL_HVD_Failure);
    TEST_ASSERT_EQUAL_INT(76, FATAL_TSMS_Failure);
    TEST_ASSERT_EQUAL_INT(77, FATAL_HW_CHECK_Failure);
    TEST_ASSERT_EQUAL_INT(78, CRITICAL_CBRB_Pressed);
    TEST_ASSERT_EQUAL_INT(79, FATAL_Battery_Task_Failure);
    TEST_ASSERT_EQUAL_INT(80, FATAL_BMU_HV_Fault);
}

void test_dtc_severity_enum(void)
{
    TEST_ASSERT_EQUAL_INT(1, DTC_Severity_FATAL);
    TEST_ASSERT_EQUAL_INT(2, DTC_Severity_CRITICAL);
    TEST_ASSERT_EQUAL_INT(3, DTC_Severity_ERROR);
    TEST_ASSERT_EQUAL_INT(4, DTC_Severity_WARNING);
}

void test_sendDTC_FATAL_BOTS_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(72, 1, 0, HAL_OK);
    sendDTC_FATAL_BOTS_Failure();
}

void test_sendDTC_FATAL_EBOX_IL_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(73, 1, 0, HAL_OK);
    sendDTC_FATAL_EBOX_IL_Failure();
}

void test_sendDTC_FATAL_BSPD_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(74, 1, 0, HAL_OK);
    sendDTC_FATAL_BSPD_Failure();
}

void test_sendDTC_FATAL_HVD_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(75, 1, 0, HAL_OK);
    sendDTC_FATAL_HVD_Failure();
}

void test_sendDTC_FATAL_TSMS_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(76, 1, 0, HAL_OK);
    sendDTC_FATAL_TSMS_Failure();
}

void test_sendDTC_FATAL_HW_CHECK_Failure_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(77, 1, 0, HAL_OK);
    sendDTC_FATAL_HW_CHECK_Failure();
}

void test_sendDTC_CRITICAL_CBRB_Pressed_emits_expected_payload(void)
{
    sendDTCMessage_ExpectAndReturn(78, 2, 0, HAL_OK);
    sendDTC_CRITICAL_CBRB_Pressed();
}

void test_sendDTC_FATAL_Battery_Task_Failure_includes_bitfield(void)
{
    /* OPEN_CIRCUIT_FAIL_BIT | READ_CELL_VOLTAGE_TEMPS_FAIL_BIT */
    const uint64_t failure_bitfield = (1U << 1) | (1U << 2);
    sendDTCMessage_ExpectAndReturn(79, 1, failure_bitfield, HAL_OK);
    sendDTC_FATAL_Battery_Task_Failure(failure_bitfield);
}

void test_sendDTC_FATAL_BMU_HV_Fault_includes_event(void)
{
    /* EV_HV_Fault == 5 in BMU_Events_t */
    sendDTCMessage_ExpectAndReturn(80, 1, 5, HAL_OK);
    sendDTC_FATAL_BMU_HV_Fault(5);
}

void test_sendDTC_FATAL_PrechargeFailed_includes_step(void)
{
    sendDTCMessage_ExpectAndReturn(31, 1, 4, HAL_OK);
    sendDTC_FATAL_PrechargeFailed(4);
}

void test_sendDTC_FATAL_DischargeFailed_includes_step(void)
{
    sendDTCMessage_ExpectAndReturn(32, 1, 1, HAL_OK);
    sendDTC_FATAL_DischargeFailed(1);
}

void test_sendDTC_FATAL_BMU_ERROR_includes_line(void)
{
    sendDTCMessage_ExpectAndReturn(24, 1, 123, HAL_OK);
    sendDTC_FATAL_BMU_ERROR(123);
}
