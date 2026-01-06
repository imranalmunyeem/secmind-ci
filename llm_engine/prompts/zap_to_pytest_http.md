You are generating ONE deterministic Python pytest security regression test.

Input will be a JSON object describing a security finding from OWASP ZAP.
Your job:
- Create a single pytest test that calls the given URL using requests.
- Add at least ONE strong assertion that reflects a security expectation.
- Must be deterministic in CI (no random, no sleeps, no flaky timing).
- Must use only: requests, pytest, re, json.
- Must include evidence logging by printing key values (status code, selected headers).
- Keep test runtime under 10 seconds.

Output format:
- Output ONLY valid Python code.
- No markdown fences.
- No explanation.

If the finding is about missing security headers (CSP, HSTS, etc.):
- Assert that the header exists and is non-empty (or contains an expected directive if reasonable).

If the finding is about information disclosure:
- Assert response body does NOT contain obvious secrets patterns (e.g., "password", "secret", "api_key") using a simple regex check.

If unsure:
- Assert status code is 200-499 and not 500+, and log headers.
