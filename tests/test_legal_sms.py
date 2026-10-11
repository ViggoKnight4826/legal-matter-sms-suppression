from legal_sms import SmsService, intake_message


def test_opted_out_number_is_suppressed_without_transport():
    service = SmsService(suppressed={"+15550000000"})
    result = service.send(intake_message("+15550000000", "MAT-1"))
    assert result == {"status": "suppressed", "matter_id": "MAT-1"}
