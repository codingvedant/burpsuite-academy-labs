# Lab: Authentication Bypass via Encryption Oracle

**Category:** Business Logic Vulnerabilities
**Difficulty:** Expert
**Lab link:** [Authentication bypass via encryption oracle](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle)

## Overview

The app uses the same encryption key for two features: the `stay-logged-in` cookie (`username:timestamp`) and the `notification` cookie (encrypts `Invalid email address: <user_input>`). The notification feature acts as an **encryption oracle** — by crafting input so the "Invalid email address: " prefix aligns on a cipher block boundary, the prefix can be stripped from the ciphertext, leaving an encrypted `administrator:timestamp` to use as the `stay-logged-in` cookie.

## Key Concepts

- **Encryption oracle:** A feature that encrypts attacker-controlled input using the application's own key — here, the notification cookie.
- **Block cipher prefix stripping:** The "Invalid email address: " prefix is 23 bytes. Padding with 9 chars makes it 32 bytes (2 full 16-byte blocks). Stripping the first 32 bytes of ciphertext removes that prefix.
- **Session cookie precedence:** The `session` cookie takes precedence over `stay-logged-in`. Removing `session` forces the app to authenticate via `stay-logged-in`.

## Exploit Flow

### Step 1 — Get wiener's stay-logged-in cookie

Log in as `wiener` with "Stay logged in" checked. Copy the `stay-logged-in` cookie.

### Step 2 — Decrypt it to get the timestamp

In Burp Decoder, paste the `stay-logged-in` value as the `notification` cookie. The app decrypts and displays it, revealing: `wiener:TIMESTAMP`.

### Step 3 — Use the notification as an encryption oracle

The notification encrypts: `Invalid email address: <input>` (23 chars prefix).

Pad to 32 bytes (2 full blocks) by prepending 9 chars:
```
Email field: xxxxxxxxxadministrator:TIMESTAMP
```

Full plaintext encrypted:
```
Block 1 (0–15):  "Invalid email ad"
Block 2 (16–31): "dress: xxxxxxxxx"
Block 3 (32–47): "administrator:TI"   ← keep from here
Block 4 (48–63): "MESTAMP" + padding  ← keep
```

### Step 4 — Strip the first 32 bytes of ciphertext

In Burp Decoder:
1. Paste notification cookie → Decode URL → Decode Base64 → switch to Hex view
2. Delete the first 32 bytes (rows `0x00` and `0x10`, i.e. the first 64 hex characters)
3. Encode as Base64 → Encode as URL

### Step 5 — Use the forged cookie

- Remove the `session` cookie (it takes precedence and would identify you as wiener)
- Set `stay-logged-in` to the forged value
- Visit `/admin` → authenticated as administrator → delete carlos → lab solved

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Still logged in as wiener on /admin | `session` cookie overrides `stay-logged-in` | Delete the `session` cookie |
| Decryption error on forged cookie | Wrong number of prefix bytes stripped | Verify prefix is exactly 32 bytes: 23 (prefix) + 9 (padding) |
| Wrong timestamp | Used a different timestamp than wiener's | Decrypt wiener's `stay-logged-in` to get exact timestamp |

## Remediation

- Use separate encryption keys for different features.
- Never expose a decryption/encryption oracle to users.
- Validate decrypted cookie contents server-side (e.g. reject tokens older than N minutes).
- Use authenticated encryption (AES-GCM) so ciphertext tampering is detected.

## Key Takeaways

- An encryption oracle + a predictable plaintext format = arbitrary ciphertext forgery.
- Block cipher boundaries are exploitable: prefix stripping works because CBC ciphertext blocks are independent.
- Always remove the `session` cookie when testing `stay-logged-in` bypass — session takes precedence.
