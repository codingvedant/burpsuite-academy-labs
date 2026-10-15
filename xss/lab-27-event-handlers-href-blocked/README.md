# Lab 27: Reflected XSS with event handlers and href attributes blocked

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS with event handlers and href attributes blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-event-handlers-and-href-attributes-blocked)

## Overview

The search functionality reflects input into HTML context. The WAF blocks all event handler attributes (`on*`) and the `href` attribute. SVG's `<animate>` element bypasses this by dynamically setting `href` at render time — the WAF only checks static HTML attributes.

## Key Concepts

- **SVG `<animate>` dynamic attribute setting:** `<animate attributeName=href values=javascript:...>` sets href at runtime, bypassing static WAF checks
- **No event handlers needed:** `javascript:` URIs execute on navigation (click), not via event handler attributes
- **SVG animation attack surface:** `<animate>`, `<animatetransform>`, `<set>` — all can manipulate attributes dynamically

## Solution

1. Search for:

```
<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click here</text></a></svg>
```

2. Click the "Click here" text on the page
3. `alert(1)` fires

## Payload Breakdown

```html
<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click here</text></a></svg>
```

- `<svg>` — container element (allowed by WAF)
- `<a>` — SVG anchor element (allowed, but can't have static `href`)
- `<animate attributeName=href values=javascript:alert(1)>` — dynamically sets `href` to `javascript:alert(1)` at render time; WAF doesn't see a static `href=` attribute
- `<text x=20 y=20>Click here</text>` — visible clickable text inside the SVG

## SVG Animation WAF Bypass Progression

| Lab | SVG Technique | What it bypasses |
|-----|--------------|-----------------|
| Lab 16 | `<animatetransform onbegin>` | Event handler blocklist (SVG-specific event) |
| Lab 27 | `<animate attributeName=href>` | Event handlers AND href blocklist (dynamic attribute) |
