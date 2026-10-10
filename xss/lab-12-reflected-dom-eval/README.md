# Lab 12: Reflected DOM XSS

**Difficulty:** Practitioner
**Type:** DOM-based (reflected source, client-side eval sink)

## Goal

Trigger `alert` by exploiting a reflected DOM XSS. The search response is JSON, and client-side JS passes it to `eval()`.

## What "Reflected DOM XSS" means

- **Reflected:** the server echoes your input back in a response.
- **DOM:** the server output alone isn't the bug - the vuln is that client-side JS feeds that reflected data into a dangerous sink. Here the sink is `eval()`. So: reflected *source*, DOM *sink*.

## The setup

1. The search term is sent to `/search-results?search=...`
2. The server returns JSON reflecting the term: `{"searchTerm":"YOUR_INPUT", "results":[...]}`
3. `searchResults.js` processes it with:
   ```javascript
   eval('(' + this.responseText + ')');
   ```

`eval` on an attacker-influenced string = code execution if you can break out of the JSON string.

## The payload - break out of the JSON string via the backslash trick

The server **escapes your `"`** to `\"`, but **does not escape backslashes**. Supply your own backslash:

```
\"-alert(1)}//
```

- Your `\` + the server's escaping of `"` collapse into `\\"`: `\\` is a literal backslash, so the `"` **closes the string** (your backslash ate their escape)
- `-alert(1)` forces `alert(1)` to execute mid-expression
- `}` closes the JSON object literal
- `//` comments out the trailing junk so there's no syntax error

`eval` runs the equivalent of `({"searchTerm":"\"-alert(1)})` -> alert fires.

Note: `<`/`>` are irrelevant here - the context is a JSON string in `eval`, not HTML.

## How I solved it

1. Searched a canary and inspected the `/search-results` JSON response - saw the term reflected, with `"` escaped to `\"`
2. Found `eval('(' + this.responseText + ')')` in searchResults.js
3. Submitted `\"-alert(1)}//`; the backslash defeated the quote-escaping, eval ran the payload, alert fired, lab solved

## Concepts to lock in

- `eval` on a server response is a classic reflected-DOM sink - escaping the quote doesn't save you if the whole string goes to `eval`.
- **Backslash-eats-the-escape:** when a filter escapes your quote by prepending `\`, prepend your own `\` so theirs becomes a literal backslash, freeing your quote. (Reused in the "single quote and backslash escaped" lab.)

## Takeaway

Never `eval` a response. Use `JSON.parse` for JSON. And escaping on the server is not a substitute for a safe client-side sink - the data still reached `eval`.
