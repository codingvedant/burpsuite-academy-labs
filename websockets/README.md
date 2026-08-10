# WebSockets

WebSockets give a full-duplex, persistent connection between browser and server over a single TCP connection - either side can send messages at any time. The connection starts as an HTTP request that is upgraded to the WebSocket protocol. The security issues fall into three classes: the messages carry injectable input, the handshake can be tampered with, and the handshake can be hijacked cross-site.

Exploited with Burp's WebSockets history (observe frames) and WebSockets Repeater (replay and edit frames on the live connection). The message and handshake labs are browser/Burp driven; the CSWSH lab is delivered from the exploit server.

[PortSwigger reference](https://portswigger.net/web-security/websockets)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Manipulating WebSocket messages to exploit vulnerabilities | Apprentice | Solved |
| 2 | Manipulating the WebSocket handshake to exploit vulnerabilities | Practitioner | Solved |
| 3 | Cross-site WebSocket hijacking | Practitioner | Solved |
