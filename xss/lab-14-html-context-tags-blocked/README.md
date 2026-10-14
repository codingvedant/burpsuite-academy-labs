# Lab 14: Reflected XSS into HTML context with most tags and attributes blocked

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS into HTML context with most tags and attributes blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-most-tags-and-attributes-blocked)

## Overview

The search functionality reflects input into HTML context, but a WAF blocks most HTML tags and event handler attributes (returns "Tag is not allowed" with a 400 status). The goal is to find allowed tags/events and deliver `print()` to a victim via the exploit server.

## Key Concepts

- **WAF bypass via fuzzing:** Burp Intruder with PortSwigger's XSS cheat sheet tag/event lists to find what the WAF missed
- **Allowed tag:** `<body>` passes the WAF (most others like `<img>`, `<svg>`, `<script>` are blocked)
- **Allowed event:** `onresize` on `<body>` — fires when the element is resized
- **Delivery trick:** `onresize` doesn't auto-fire, so use an iframe whose `onload` changes its own width → triggers resize inside the framed page

## Solution

1. Send search request to Burp Intruder, fuzz `<§§>` with the XSS cheat sheet tag list — look for 200 responses (not 400)
2. Find `<body>` is allowed
3. Fuzz `<body §§=1>` with the events list — find `onresize` returns 200
4. Go to exploit server, set the body to:

```html
<iframe src="https://LAB-ID.web-security-academy.net/?search=%3Cbody+onresize%3Dprint()%3E" onload="this.style.width='100px'">
```

5. Store → Deliver to victim

## Payload Breakdown

```html
<iframe src="LAB/?search=<body onresize=print()>" onload="this.style.width='100px'">
```

- The iframe loads the search page with `<body onresize=print()>` reflected in the response
- `onload` fires and changes the iframe width → `<body>` inside resizes → `onresize` fires → `print()` executes in the lab's origin
