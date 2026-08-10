# Lab 1: Manipulating WebSocket messages to exploit vulnerabilities

**Difficulty:** Apprentice

## Goal

The live chat sends messages over a WebSocket, and they are rendered to a support agent. Get an XSS payload to execute in the agent's browser.

## Exploit

Send a chat message, intercept the outgoing WebSocket frame in Burp, and replace the message text with an XSS payload.

```
<img src=1 onerror='alert(1)'>
```

## Steps

1. Open the live chat and send a normal message (e.g. `hello`)
2. In Burp, go to Proxy > WebSockets history and find the outgoing frame, e.g. `{"message":"hello"}`
3. Send it to WebSockets Repeater
4. Replace the message text with the XSS payload and send
5. The payload is rendered unsanitised in the support agent's browser and the alert fires

## Why it works

WebSocket messages are just another channel carrying user input. The chat renders the message text without sanitisation, so the same XSS that works over HTTP works here - the only difference is the transport. Burp's WebSockets history and Repeater let you edit and replay frames on the live connection.

## Takeaway

Data arriving over a WebSocket is still untrusted input. It must be validated and output-encoded exactly like HTTP request data. The transport does not change the vulnerability class.

## Note on automation

Browser/Burp driven - the payload must be rendered by the agent's browser to fire, so there is no Python solve. The payload above is the exploit.
