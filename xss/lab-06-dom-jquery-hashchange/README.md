# Lab 6: DOM XSS in jQuery selector sink using a hashchange event

**Difficulty:** Apprentice
**Type:** DOM-based

## Goal

Deliver an exploit that calls `print()` in the victim's browser. The home page runs a `hashchange` handler that feeds `location.hash` into a jQuery `$()` selector.

## The key insight

The vulnerable handler:

```javascript
$(window).on('hashchange', function(){
    var post = $('section.blog-list h2:contains(' + decodeURIComponent(location.hash.slice(1)) + ')');
    if (post) post.get(0).scrollIntoView();
});
```

- **Source:** `location.hash`
- **Sink:** jQuery `$()` selector (shows as `jQuery.init` in DOM Invader)
- **Trigger:** the `hashchange` event

Two things make this one distinct:

1. **jQuery `$()` creates elements.** If the string passed to `$()` contains an HTML tag, jQuery builds it as HTML instead of selecting. So a hash of `<img src=1 onerror=print()>` makes jQuery create that img -> `onerror` fires. (`<script>` wouldn't run - use an event-handler element, same as innerHTML.)
2. **`hashchange` only fires when the hash *changes*.** A link with the payload already in the hash does nothing (no change event). The hash must change *after* load.

## Exploit (exploit server -> deliver to victim)

```html
<iframe src="https://LAB-ID.web-security-academy.net/#" onload="this.src+='<img src=1 onerror=print()>'"></iframe>
```

Chain:
1. iframe loads the home page with an empty `#` (harmless)
2. `onload` fires after load, then `this.src += '<img...>'` appends the payload - changing `location.hash` on the already-loaded page
3. that change fires `hashchange` -> the payload goes into `$()` -> jQuery builds the `<img>` -> `onerror` runs `print()`

Store on the exploit server and Deliver to victim.

## Finding it with DOM Invader

Enable DOM Invader + "Inject canary into all sources" in Burp's browser, load the home page, then **change the hash in the URL bar** (e.g. `#x`, Enter, `#y`, Enter). The event-gated sink only registers once a real `hashchange` fires - then `jQuery.init` appears under Sinks (Event: `hashchange`) with an Exploit button. Note: navigating straight to a hashed URL does NOT fire the event; you must change the hash on a loaded page.

## Why delivery is required

Unlike the document.write / innerHTML labs (which solve the instant the payload runs in your own browser), this lab's success condition is `print()` in the **victim's** browser. DOM Invader's Exploit button only fires it locally - the solve needs the exploit server to deliver the hash-changing iframe.

## Takeaway

Don't concatenate untrusted input into jQuery selectors - `$()` is an HTML-creation sink, not just a lookup. Validate against an allowlist, or use safe DOM lookups. And remember event-gated sinks: a value sitting in the URL is not the same as the event that reads it firing.
