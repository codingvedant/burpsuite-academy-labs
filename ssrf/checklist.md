# SSRF Testing Checklist

## Recon

1. **Is there a parameter that takes a URL?**
   - Stock check features, webhook URLs, PDF generators, image fetchers, import-from-URL
   - Check for parameters like `url=`, `stockApi=`, `src=`, `dest=`, `redirect=`, `uri=`
   - Look at POST bodies, not just query strings

2. **What happens when you change the URL?**
   - Does the server fetch it? Check response time differences
   - Can you point it at a Burp Collaborator to confirm out-of-band requests?

3. **Can you reach localhost?**
   - Try `http://localhost/admin` or `http://127.0.0.1/admin`
   - Works? Go to [Exploit](#exploit)
   - Blocked? Go to [Bypass](#bypass---based-on-what-gets-blocked)

## Bypass - based on what gets blocked

**Server blocks `127.0.0.1` / `localhost` (blacklist)**

Try alternative representations:
- `127.1` (shorthand)
- `2130706433` (decimal)
- `017700000001` (octal)
- `127.0.0.1` with URL-encoded characters
- Register a domain that resolves to 127.0.0.1

Blocked path like `/admin`?
- URL encode: `/%61dmin`
- Double encode: `/%2561dmin`
- Case variation: `/Admin`, `/ADMIN`

**Server only allows a specific domain (whitelist)**

Exploit URL parsing ambiguity:
- `@` trick: `https://allowed.com@evil-host` (treats allowed.com as credentials)
- `#` trick: `https://evil-host#allowed.com` (allowed.com becomes a fragment)
- DNS: `https://allowed.com.evil-host` (subdomain of your domain)
- Combine with URL encoding: `http://localhost%2523@allowed.com`
- Stack multiple tricks together for best results

**Both direct and parsing tricks are blocked?**

Look for open redirects on allowed domains:
- `/product/nextProduct?path=http://internal-target`
- `/login?redirect=http://internal-target`
- Feed the redirect URL to the SSRF - filter sees the allowed domain, server follows the redirect

## Exploit

Once you have SSRF working:
- Scan internal networks: `192.168.0.0/24`, `10.0.0.0/8`, `172.16.0.0/12`
- Access admin panels that trust localhost
- Hit cloud metadata: `http://169.254.169.254/latest/meta-data/` (AWS)
- Read internal API docs, configuration endpoints
- Chain with other vulns for RCE

## Prevention

- Whitelist allowed URLs/domains (not blacklist)
- Don't follow redirects in server-side requests
- Validate the resolved IP address, not just the hostname
- Use a firewall to block outbound requests to internal ranges
