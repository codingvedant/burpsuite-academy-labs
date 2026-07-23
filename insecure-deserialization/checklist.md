# Insecure Deserialization Testing Checklist

## Recon

1. **Identify serialized data** in cookies, hidden form fields, API responses
   - PHP serialized: starts with `O:` or `a:` (or base64-encoded version)
   - Java serialized: starts with `ac ed` (hex) or `rO0` (base64)
   - JSON, XML, YAML can also carry serialized objects
2. **Decode the data** - check for base64, URL encoding, or both
3. **Map the object structure** - what fields exist, what types are they?

## Exploitation path

```
Found serialized data?
|
+-- Can you modify attributes?
|   +-- Change role/admin/privilege flags (Lab 1)
|   +-- Swap data types to abuse loose comparison (Lab 2)
|       - PHP: i:0 == "any_string" with loose comparison
|
+-- Does the app act on object fields?
|   +-- Change file paths, URLs, or references (Lab 3)
|       - avatar_link, file_path, etc. -> point to target file
|       - Trigger the action (delete account, cleanup, etc.)
|
+-- Can you inject a different object type?
|   +-- Look for classes with magic methods (__destruct, __wakeup, __toString)
|   +-- Check backup files, source code for available classes (Lab 4)
|   +-- Build a serialized object of that class with malicious field values
|
+-- Is it Java deserialization?
    +-- Identify libraries on the classpath (error messages, response headers)
    +-- Use ysoserial to generate gadget chain payloads (Lab 5)
        - CommonsCollections4 for Apache Commons Collections 4.x
        - CommonsCollections1/6 for Apache Commons Collections 3.x
        - Try multiple chains if unsure which version
    +-- Base64-encode and URL-encode the payload
    +-- Replace the session cookie and send
```

## Quick reference

| Technique | When to use |
|-----------|------------|
| Attribute tampering | Object has role/admin/privilege fields |
| Type juggling | App uses loose comparison (PHP `==`) on tokens |
| Functionality abuse | App performs file/system operations based on object fields |
| Object injection | Source code or backups reveal classes with dangerous magic methods |
| Gadget chains (ysoserial) | Java app with known libraries (Commons Collections, Spring, etc.) |

## Tips

- A 500 error after injecting a payload doesn't mean it failed - the command may have executed during deserialization before the error
- Always URL-decode cookies before base64-decoding (cookies often have `%3d` instead of `=`)
- PHP string length fields must match: `s:5:"admin"` - the 5 must equal the string length
- For Java on modern JVMs (16+), ysoserial needs `--add-opens` flags to access internal modules
