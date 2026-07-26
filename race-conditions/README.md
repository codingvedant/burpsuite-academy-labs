# Race Conditions

Exploiting timing gaps in how applications process concurrent requests. When multiple threads interact with the same data before updates are saved, you can bypass business logic limits, skip authentication steps, and abuse partially constructed objects.

The key technique is the single-packet attack (HTTP/2), which sends many requests in one TCP packet so they arrive at the server simultaneously, eliminating network jitter.

[PortSwigger reference](https://portswigger.net/web-security/race-conditions)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Limit overrun race conditions | Apprentice | Solved |
| 2 | Bypassing rate limits via race conditions | Practitioner | Solved |
| 3 | Multi-endpoint race conditions | Practitioner | Solved |
| 4 | Single-endpoint race conditions | Practitioner | Solved |
| 5 | Partial construction race conditions | Practitioner | Solved |
| 6 | Exploiting time-sensitive vulnerabilities | Practitioner | Solved |
