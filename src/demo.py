import os

from legal_sms import SmsService, deadline_follow_up, intake_message, signed_delivery


def main() -> None:
    destination = os.environ.get("DEMO_PHONE_NUMBER")
    if not destination:
        raise SystemExit("Set DEMO_PHONE_NUMBER before running the demo")
    service = SmsService(suppressed={"+15550000000"})
    for message in (intake_message(destination, "MAT-104"), signed_delivery(destination, "MAT-104"), deadline_follow_up(destination, "MAT-104")):
        print(service.send(message))


if __name__ == "__main__":
    main()
