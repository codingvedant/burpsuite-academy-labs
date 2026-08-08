# CSRF (Cross-Site Request Forgery)

Tricking a logged-in victim's browser into sending a state-changing request they never intended. It works because browsers automatically attach cookies to requests, even ones triggered from an attacker's site, so if the server trusts the session cookie alone to authorize an action, that action can be forged.

Every lab targets the same change-email action and adds one defense - a CSRF token, a SameSite cookie restriction, or a Referer check - then exploits a flaw in how that defense is implemented.

CSRF is exploited by hosting an HTML page on the exploit server and delivering it to the victim, so these entries document the exploit HTML and the bypass technique. Where the exploit server's store/deliver API can be driven over HTTP, a solve.py automates delivery.

[PortSwigger reference](https://portswigger.net/web-security/csrf)

## Basic

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | CSRF vulnerability with no defenses | Apprentice | Solved |

## Bypassing token validation

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 2 | CSRF where token validation depends on request method | Practitioner | Solved |
| 3 | CSRF where token validation depends on token being present | Practitioner | Not started |
| 4 | CSRF where token is not tied to user session | Practitioner | Not started |
| 5 | CSRF where token is tied to non-session cookie | Practitioner | Not started |
| 6 | CSRF where token is duplicated in cookie | Practitioner | Not started |

## Bypassing SameSite restrictions

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 7 | SameSite Lax bypass via method override | Practitioner | Not started |
| 8 | SameSite Strict bypass via client-side redirect | Practitioner | Not started |
| 9 | SameSite Strict bypass via sibling domain | Practitioner | Not started |
| 10 | SameSite Lax bypass via cookie refresh | Practitioner | Not started |

## Bypassing Referer-based defenses

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 11 | CSRF where Referer validation depends on header being present | Practitioner | Not started |
| 12 | CSRF with broken Referer validation | Practitioner | Not started |
