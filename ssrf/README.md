# Server-Side Request Forgery (SSRF)

Making the server send HTTP requests to unintended locations on your behalf. If an application fetches data from a URL you control (like a stock check API), you can redirect that request to internal services, localhost admin panels, or cloud metadata endpoints that are normally unreachable from the outside.

The labs progress from basic SSRF against localhost and internal systems, through bypassing blacklist and whitelist filters, to using open redirects to chain past SSRF defenses.

[PortSwigger reference](https://portswigger.net/web-security/ssrf)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Basic SSRF against the local server | Apprentice | Solved |
| 2 | Basic SSRF against another back-end system | Apprentice | Solved |
| 3 | SSRF with blacklist-based input filter | Practitioner | Solved |
| 4 | SSRF with whitelist-based input filter | Practitioner | Solved |
| 5 | SSRF with filter bypass via open redirection | Practitioner | Solved |
