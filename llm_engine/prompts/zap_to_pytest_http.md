Generate ONE deterministic Python pytest test from a ZAP finding.

Rules:
- Output ONLY valid Python code (no markdown).
- Must include: import requests
- Must define: def test_...():
- Must include at least ONE assert statement.
- Keep runtime under 10 seconds (use timeout).
- Log evidence using print(status_code) and print(selected headers).
