# API Testing

Attacking REST-style APIs by discovering their structure and abusing endpoints the frontend never uses. Once you can see how an API maps input to internal objects and how it builds internal requests, you can delete users, change prices, grant yourself discounts, and hijack password resets.

The recurring theme is that APIs often trust the client far more than the UI does. Fields that never appear in the browser, HTTP methods the app never calls, and internal query parameters the server builds from your input are all fair game.

[PortSwigger reference](https://portswigger.net/web-security/api-testing)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Exploiting an API endpoint using documentation | Apprentice | Solved |
| 2 | Finding and exploiting an unused API endpoint | Practitioner | Solved |
| 3 | Exploiting a mass assignment vulnerability | Practitioner | Solved |
| 4 | Exploiting server-side parameter pollution in a query string | Practitioner | Solved |
