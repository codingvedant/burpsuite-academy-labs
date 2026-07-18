# Path Traversal

Reading arbitrary files from the server by manipulating file paths in application requests. Also called directory traversal or dot-dot-slash attacks. If an application uses user input to construct file paths without proper validation, you can break out of the intended directory and read sensitive files like `/etc/passwd` or application source code.

The labs start with a basic `../` traversal and then layer on different server-side defenses - absolute path checks, sequence stripping, URL encoding, path prefix validation, and extension whitelisting.

[PortSwigger reference](https://portswigger.net/web-security/file-path-traversal)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | File path traversal, simple case | Apprentice | Solved |
| 2 | File path traversal, traversal sequences blocked with absolute path bypass | Practitioner | Solved |
| 3 | File path traversal, traversal sequences stripped non-recursively | Practitioner | Solved |
| 4 | File path traversal, traversal sequences stripped with superfluous URL-decode | Practitioner | Solved |
| 5 | File path traversal, validation of start of path | Practitioner | Solved |
| 6 | File path traversal, validation of file extension with null byte bypass | Practitioner | Solved |
