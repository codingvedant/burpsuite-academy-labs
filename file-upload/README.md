# File Upload Vulnerabilities

Exploiting insecure file upload handling to get remote code execution on the server. The core idea is simple: if a server lets you upload a file and then serves it back in a way that gets executed (like a `.php` file in a web root), you can upload a web shell and run arbitrary commands.

These labs progressively add more server-side defenses like content-type checks, extension blacklists, and directory restrictions. Each script finds a way around them.

[PortSwigger reference](https://portswigger.net/web-security/file-upload)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Remote code execution via web shell upload | Apprentice | |
| 2 | Web shell upload via Content-Type restriction bypass | Apprentice | |
| 3 | Web shell upload via path traversal | Practitioner | |
| 4 | Web shell upload via extension blacklist bypass | Practitioner | |
| 5 | Web shell upload via obfuscated file extension | Practitioner | |
| 6 | Remote code execution via polyglot web shell upload | Practitioner | |
| 7 | Web shell upload via race condition | Expert | |
