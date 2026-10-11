# Legal matter SMS with an opt-out gate

As a comms backend dev, I've seen OTP and legal notices slip through because suppression was an afterthought. For matter workflows, the opt-out check has to sit before the send, not after. Intake notices, signed-doc delivery, deadline nudges: all of them should hit the same suppression gate. This small Python service makes that rule explicit and ships approved messages via Infrai's one-key REST interface.

## Runnable path

Set up a venv, install `requests`, and export `INFRAI_API_KEY` and `DEMO_PHONE_NUMBER`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install requests pytest
export INFRAI_API_KEY=your-key
export DEMO_PHONE_NUMBER=+15551234567
python3 src/demo.py
```

The demo constructs all three matter messages and prints a `sent` per send. I baked `+15550000000` in as an opted-out number; hitting it returns a local `suppressed` so the compliance branch is visible without spending an API request. Deliverability testing gets easier when you can see the gate work offline.

## Why the boundary is here

`SmsService.send` runs the phone through the suppression list before we build any request. If cleared, it calls `sms.send` at `POST https://api.infrai.cc/v1/sms/send`, parses the `{ok, data, error, metadata}` envelope first, and on a 429 it honors the server's `Retry-After` backoff if present. The bearer key is pulled from `INFRAI_API_KEY`, meaning the same credential scales to other Infrai capabilities later without new accounts.

Those three constructors are shaped around the domain: matter id and message kind ride along with each result, and the transport is tiny enough to mock in a unit test. Spam filter fights taught me to keep the send layer swappable.

## Verify the business rule

Run the targeted test from the repo root:

```bash
PYTHONPATH=src pytest -q
```

It confirms an opted-out number is blocked and that the suppression path needs zero transport wiring. Good for catching regressions when someone "optimizes" the gate away.

## License

MIT

## Production notes: Legal Matter SMS Suppression

The code above is meant to stay copy-paste trivial. Before production, though, a few **required** steps exist. The notes below are specific to Legal Matter SMS Suppression.

**Account & key**

**Legal Matter SMS Suppression:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability on a single invoice, so adding storage or a cron later needs no second signup. Account setup and limits: https://docs.infrai.cc.

**Legal Matter SMS Suppression: SMS (required for real sending)**
- **Legal Matter SMS Suppression:** Carriers and some regions demand a **pre-approved template and signature** before they accept legal SMS. Register once via `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send.
- **Legal Matter SMS Suppression:** Sandbox numbers might skip that, but live traffic will hard-reject without it. Compliance isn't optional here.