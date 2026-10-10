# Lab 11: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded

**Difficulty:** Apprentice
**Type:** DOM-based (client-side template injection)

## Goal

Trigger `alert` by injecting an AngularJS expression. The page uses AngularJS, and the search input is reflected into an `ng-app` region where Angular evaluates `{{ }}`.

## The key insight

The site has an `ng-app` directive, so Angular scans that DOM region and evaluates any `{{ expression }}` it finds - **client-side, after the HTML is parsed**. The filter HTML-encodes `<`, `>`, and `"`, which kills tag injection and attribute breakout - but Angular doesn't care about those characters. You don't need HTML; you inject an **Angular expression** that runs JavaScript.

- **Context:** inside an AngularJS `ng-app` region (template injection, not HTML XSS)
- **Filter:** `<`, `>`, `"` encoded - irrelevant to an Angular expression

## Exploit

```
{{$on.constructor('alert(1)')()}}
```

- `$on` is a method on the Angular scope
- `$on.constructor` is JavaScript's `Function` constructor
- `Function('alert(1)')` builds a function whose body is `alert(1)`
- the trailing `()` calls it -> `alert(1)` runs

Essentially the Angular-expression route to `Function('alert(1)')()` without any blocked characters.

## How I solved it

1. Spotted `ng-app` in the page source (AngularJS in use)
2. Confirmed expression evaluation: `{{7*7}}` rendered as `49` (not the literal string)
3. Submitted `{{$on.constructor('alert(1)')()}}` in the search box - Angular evaluated it, built and called the function, alert fired, lab solved

## Why DOM Invader can't find this

DOM Invader hooks standard DOM API sinks (innerHTML, document.write, eval, setAttribute). AngularJS XSS is **template injection** - the dangerous step is Angular evaluating `{{ }}`, which isn't a DOM sink, so DOM Invader doesn't flag it. The tell is `ng-app` in the source + a `{{7*7}}` -> `49` test, not the tool.

## The concept to lock in

A client-side template engine is its own injection context. If input lands in an `ng-app` region you have template injection, and HTML encoding is irrelevant because the engine evaluates expressions after parsing. This is the gateway to the AngularJS sandbox-escape family (1.6+ removed the sandbox, simplifying the payload).

## Takeaway

Never place untrusted input inside a client-side template region. Keep user data out of `ng-app` scopes, or use `ng-non-bindable`, and prefer server-side rendering with proper encoding over interpolating untrusted values into templates.
