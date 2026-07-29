# API Testing Checklist

## Recon

1. **Find the API docs** - try `/api`, `/api/`, `/swagger/index.html`, `/openapi.json`, `/api/swagger/v1/swagger.json`. Burp Scanner can crawl for these
2. **Map endpoints from JS** - use JS Link Finder or read the JavaScript the pages load. API paths are often hardcoded there
3. **Watch the traffic** - browse the app normally and note every `/api/...` request in Proxy history
4. **Note the base pattern** - endpoints like `/api/products/1/price` hint at `/api/products/:id/:field`

## Exploitation path

```
Found an API endpoint?
|
+-- Is there documentation? (/api, /swagger, /openapi.json)
|   +-- Read the docs, find privileged operations (Lab 1)
|       - DELETE /api/user/:username to remove accounts
|
+-- Does the frontend only use one HTTP method?
|   +-- Send OPTIONS to list allowed methods (Lab 2)
|       - Try PATCH/PUT/POST/DELETE on read-only endpoints
|       - PATCH a price/quantity field the UI never edits
|
+-- Does a GET response expose fields the POST doesn't show?
|   +-- Mass assignment: resubmit those fields in your write request (Lab 3)
|       - chosen_discount, isAdmin, roleid, price
|       - Server binds all submitted fields to the object
|
+-- Does your input get embedded in a server-side API request?
    +-- Server-side parameter pollution (Lab 4)
        - Inject %26field=x (&) to add parameters
        - Inject %23 (#) to truncate appended parameters
        - Read error messages to map valid field names
        - Leak reset tokens, override internal params
```

## Injection characters (URL-encoded)

| Character | Encoded | Effect |
|-----------|---------|--------|
| `&` | `%26` | Add a new parameter |
| `=` | `%3d` | Set a parameter value |
| `#` | `%23` | Truncate the rest of the server-side query |
| `?` | `%3f` | Start a new query string |

## Common gotchas

- APIs often reject anything but `Content-Type: application/json` - set it explicitly
- Send numeric fields as numbers (`"price": 0`), not strings (`"price": "$0.00"`)
- OPTIONS responses (or the `Allow` header) reveal methods the UI never calls
- GET responses are recon gold - they leak the internal field names for mass assignment
- Error messages ("Invalid field", "Parameter not found") map out the internal API for you
- For SSPP, test one injection character at a time and watch how the response changes

## Tips

- Trigger a reset/action on your own account first to learn the exact URL and parameter names, then swap in the target's values
- A reset token is the key to the new-password page - it almost always rides in a query parameter
- Compare valid vs invalid input responses to spot which endpoints leak information
