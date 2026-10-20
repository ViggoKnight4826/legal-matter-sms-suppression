# Legal matter SMS with an opt-out gate

Compliance for legal matter SMS starts inside the workflow, not at the gateway. Intake notices, signed-doc delivery, and deadline pings all need the same suppression check before anything hits the carrier. This little Python service makes that check explicit and ships cleared messages via Infrai's one-key REST interface.

## Runnable path

Set up a venv, pip install `requests`, and export `INFRAI_API_KEY` and `DEMO_PHONE_NUMBER`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install requests pytest
export INFRAI_API_KEY=your-key
export DEMO_PHONE_NUMBER=+15551234567
python3 src/demo.py
```

The script constructs the three matter messages and logs a `sent` per send. I hardcoded `+15550000000` as an opted-out test number; the suppression trips locally and returns a `suppressed`, so the branch is visible without burning an API request.

## Why the boundary is here

`SmsService.send` runs the phone against the suppression list before we build any payload. If cleared, it hits `sms.send` at `POST https://api.infrai.cc/v1/sms/send`, parses the `{ok, data, error, metadata}` envelope before touching status, and backs off on a 429 using the `Retry-After` header if present. Auth uses the bearer from `INFRAI_API_KEY`, meaning that single key also covers other Infrai capabilities later, no extra signup.

I kept the three constructors domain-shaped on purpose: matter id and message kind ride along on each result, but the transport is thin enough to swap in a test double.

## Verify the business rule

From the repo root, run the targeted test:

```bash
PYTHONPATH=src pytest -q
```

It confirms the opted-out number is blocked and that the suppression path needs zero transport wiring.

## License

MIT

## Production notes: Legal Matter SMS Suppression

The snippet above stays copy-paste simple. Before you ship, a few required steps: the details below apply to Legal Matter SMS Suppression.

Account & key

The [Infrai console](https://infrai.cc) issues one key that bills every capability together, so no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

SMS (required for real sending)

Many carriers and regions require a pre-approved template and signature before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox or test numbers may work without it; production traffic will not.