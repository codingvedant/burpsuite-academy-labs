# Race Conditions Testing Checklist

## Recon

1. **Identify security-critical operations** - login, checkout, coupon redemption, email change, registration, password reset
2. **Look for shared state** - operations that read and write to the same data (counters, balances, tokens)
3. **Check for session locking** - send parallel requests on the same session. If they serialize, use different sessions
4. **Note the protocol** - HTTP/2 enables single-packet attacks for precise timing

## Exploitation path

```
Found a security-critical operation?
|
+-- Does it enforce a limit? (coupons, rate limits, balances)
|   +-- Limit overrun: send 20+ identical requests in parallel (Lab 1)
|   +-- Rate limit bypass: send all attempts in one packet (Lab 2)
|
+-- Does it span multiple endpoints? (cart + checkout, email change + confirmation)
|   +-- Multi-endpoint race: fire both endpoints simultaneously (Lab 3)
|       - Add cheap item, race checkout against adding expensive item
|       - Use connection warming to align timing
|
+-- Does it write then read on the same endpoint? (email change, password reset)
|   +-- Single-endpoint race: send parallel requests with different values (Lab 4)
|       - Email change: one to your email, one to target email
|       - The confirmation link goes to your inbox but for the target email
|
+-- Does it create objects in multiple steps? (registration with confirmation)
|   +-- Partial construction: race registration against confirmation (Lab 5)
|       - Send token[]= (empty array) to match uninitialized token
|       - Need hundreds of confirmation attempts per registration
|
+-- Does it generate tokens from timestamps? (password reset, CSRF tokens)
    +-- Time-sensitive: send parallel resets from different sessions (Lab 6)
        - Same-timestamp requests produce identical tokens
        - Use your token with the victim's username
```

## Techniques

| Technique | Tool | When to use |
|-----------|------|------------|
| Single-packet attack (HTTP/2) | Burp Repeater tab group | Precise timing, few requests |
| Turbo Intruder with gates | Turbo Intruder | Many requests, complex patterns |
| Connection warming | GET / before attack | Reduce timing jitter on first request |
| Multiple sessions | Different cookies | Bypass per-session request locking |

## Tips

- HTTP/2 single-packet attack is the most reliable timing method
- Connection warming eliminates backend connection setup delays
- Per-session locking (common in PHP) forces you to use separate sessions
- Partial construction windows are tiny - send hundreds of attempts
- Time-sensitive attacks may need multiple runs to hit the same timestamp
- Always check response length/status differences to spot the winning request
