# Prototype Pollution

Adding or modifying properties on JavaScript's `Object.prototype` so that every object in the app inherits attacker-controlled values. When a vulnerable app merges user input into objects without filtering `__proto__`, `constructor`, and `prototype`, you can plant properties that later flow into a dangerous sink.

Every attack has three parts: a **source** (input you control), a **sink** (a function or DOM operation that does something dangerous with a property), and a **gadget** (the property the app reads from an object expecting it to be undefined).

Client-side labs are driven in the browser (URL params, DOM Invader, JS console) and lead to DOM XSS, so those entries document the payload and gadget chain instead of a Python script. Server-side labs send JSON to the backend and are automated the usual way.

[PortSwigger reference](https://portswigger.net/web-security/prototype-pollution)

## Client-side

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Client-side prototype pollution via browser APIs | Practitioner | Solved |
| 2 | DOM XSS via client-side prototype pollution | Apprentice | Solved |
| 3 | DOM XSS via an alternative prototype pollution vector | Practitioner | Solved |
| 4 | Client-side prototype pollution via flawed sanitization | Practitioner | Solved |
| 5 | Client-side prototype pollution in third-party libraries | Practitioner | Solved |

## Server-side

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 6 | Privilege escalation via server-side prototype pollution | Practitioner | Solved |
| 7 | Detecting server-side prototype pollution without polluted property reflection | Practitioner | Solved |
| 8 | Bypassing flawed input filters for server-side prototype pollution | Practitioner | Solved |
| 9 | Remote code execution via server-side prototype pollution | Practitioner | Solved |
| 10 | Exfiltrating sensitive data via server-side prototype pollution | Expert | Not started |
